import functools
import logging
from srs.models import Flashcard, FlashcardSnapshot, Entry
from django.utils import timezone
from datetime import timedelta
from asyncio import streams
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
from random import Random
from copy import deepcopy
import math

from asyncio import Lock

class SrsException(Exception):
  
  pass


from abc import ABC
class SrsBridge(ABC):
  async def srs_new_card(self, html, undo_available):
    pass
  async def srs_reviews_done(self):
    pass

MAX_LEITNER_BOX_ON_FAIL = 3
MAX_LEITNER_BOX = 7
LEITNER_INTERVAL_BASE = 1
LEITNER_INTERVAL_MULTIPLIER = 2
LEITNER_INTERVAL_MAX_DEVIATION = 0.2
LEITNER_INTERVAL_DEVIATION_VARIANCE = 0.15

def generate_leitner_interval(box):
  if box == 0:
    return 1
  
  base = LEITNER_INTERVAL_BASE * LEITNER_INTERVAL_MULTIPLIER ** box
  deviation = Random().gauss(1, LEITNER_INTERVAL_DEVIATION_VARIANCE)
  clamped_deviation = min(1 + LEITNER_INTERVAL_MAX_DEVIATION, max(1 - LEITNER_INTERVAL_MAX_DEVIATION, deviation))
  return math.ceil(base * clamped_deviation)


class SrsReview():
  logger = logging.getLogger(__name__)

  _review_in_progress = False
  review_in_progress = property(lambda self: self._review_in_progress)

  _user = None
  user = property(lambda self: self._user)

  MAX_UNDO_HISTORY_LENGTH = 20
  undo_history: list[FlashcardSnapshot]

  def __init__(self, bridge: SrsBridge):
    self.bridge = bridge

  # Helpers
  def __require_in_progress():
    def decorator(fn):
      @functools.wraps(fn)
      async def wrapper(self):
        if self.review_in_progress:
          await fn()
        else:
          raise SrsException('The review has not yet been started.')
      return wrapper
    return decorator
  
  async def __send_current_card(self):
    if self.current_card:
      self.logger.debug('Sending card %d to user "%s"', self.current_card.pk, self.user.username)
      html = render_to_string('srs/card.html', {
        'entry': self.current_card.entry,
        'user': self.user
      })
      await self.bridge.srs_new_card(html, len(self.undo_history) > 0)
      return True
    else:
      self.logger.debug('User "%s" has finished his reviews.', self.user.username)
      await self.bridge.srs_reviews_done()
      self._review_in_progress = False
      return False
    

  async def __next_card(self):
    # TODO: Maybe eventually retrieve them in chunks
    self.current_card = await Flashcard.objects.expired(self.user, timezone.now()).prefetch_everything().afirst()
    await self.__send_current_card()

  # Handlers
  async def start(self, user):
    if self.review_in_progress:
      self.logger.warn('User "%s" tried to start an SRS review when it had already been started.', user.username)
      raise SrsException('The review had already been started.')
    
    self._user = user
    self._review_in_progress = True

    self.logger.debug('User "%s" is starting a review.', user.username)

    self.undo_history = []
    await self.__next_card()

  __require_in_progress()
  async def stop(self):
    self.logger.debug('User "%s" has prematurely abandoned the review.', self.user.username)

  __require_in_progress()
  async def answer(self, confidence):
    self.logger.debug('User "%s" answered card "%d" with confidence %d', self.user.username, self.current_card.entry.ent_seq, confidence)
    
    snapshot = self.current_card.get_snapshot()

    now = timezone.now()

    if confidence > 0:
      self.current_card.leitner_box = min(MAX_LEITNER_BOX, self.current_card.leitner_box + 1)
    else:
      self.current_card.leitner_box = min(MAX_LEITNER_BOX_ON_FAIL, max(0, self.current_card.leitner_box - 1))

    self.current_card.expiration_date = now.date() + timedelta(days=generate_leitner_interval(self.current_card.leitner_box))
    self.current_card.last_review_timestamp = now
    await self.current_card.asave()

    if len(self.undo_history) >= SrsReview.MAX_UNDO_HISTORY_LENGTH:
      self.undo_history.pop()
    self.undo_history.append(snapshot)
    
    await self.__next_card()

  __require_in_progress()
  async def undo(self):
    if len(self.undo_history) == 0:
      self.logger.debug('User "%s" has requested an undo operation when there are no undoable cards.', self.user.username)
      raise SrsException('No cards to undo!')
    
    self.logger.debug('User "%s" requested an undo.', self.user.username)
    snapshot = self.undo_history.pop()

    flashcard = await Flashcard.objects.filter(pk=snapshot.flashcard_pk).prefetch_everything().afirst()
    if flashcard is None:
      self.logger.warn("Snapshot of non-existing flashcard for user %s!")
      raise SrsException('Flashcards were modified outside the SRS review.')
    
    flashcard.leitner_box = snapshot.leitner_box
    flashcard.expiration_date = snapshot.expiration_date
    flashcard.last_review_timestamp = snapshot.last_review_timestamp
    await flashcard.asave()
      
    self.current_card = flashcard
    await self.__send_current_card()