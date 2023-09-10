import functools
import logging
from srs.models import Flashcard
from django.utils import timezone
from asyncio import streams
from channels.db import database_sync_to_async

class SrsException(Exception):
  pass

from abc import ABC
class SrsBridge(ABC):
  async def srs_new_card(self, html):
    pass
  async def srs_reviews_done(self):
    pass

class SrsReview():
  FLASHCARD_LOAD_CHUNK_SIZE = 10

  logger = logging.getLogger(__name__)

  _review_in_progress = False
  review_in_progress = property(lambda self: self._review_in_progress)

  _user = None
  user = property(lambda self: self._user)

  def __init__(self, bridge: SrsBridge):
    self.bridge = bridge

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

  async def start(self, user):
    self.logger.info("Starting review")
    if self.review_in_progress:
      self.logger.info('User "%s" tried to start an SRS review when it had already been started.', user.username)
      raise SrsException('The review had already been started.')
    
    self._user = user
    self._review_in_progress = True

    expired = [x async for x in Flashcard.objects.expired(self.user, timezone.now())[:SrsReview.FLASHCARD_LOAD_CHUNK_SIZE]]
    print(expired)

    if len(expired) == 0:
      self.logger.info('User "%s" has no pending reviews.', user.username)
      return await self.bridge.srs_reviews_done()
    
    await self.bridge.srs_new_card("test")


  __require_in_progress()
  async def stop(self):
    pass

  __require_in_progress()
  async def answer(self, confidence):
    pass

  __require_in_progress()
  async def undo(self):
    pass


