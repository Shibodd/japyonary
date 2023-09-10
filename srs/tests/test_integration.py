from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from users.models import User

from django.utils import timezone
from datetime import timedelta

from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from srs.consumers import SrsConsumer
from django.urls import path
import logging

import dictionary.management.commands.jmdict_xml as jmdict
from dictionary.management.commands.load_dictionary import update_db as update_db_from_jmd

from srs.models import Flashcard
from dictionary.models import Entry

from asyncio import sleep

application = AuthMiddlewareStack(URLRouter([
  path('ws/', SrsConsumer.as_asgi())
]))

class MessageWebsocketCommunicator(WebsocketCommunicator):
  async def send_message_to(self, message, **payload):
    await self.send_json_to({
      'message': message,
      'payload': payload
    })

  async def receive_message_from(self):
    content = await self.receive_json_from()
    return (content['message'], content.get('payload', {}))

class SrsIntegrationTests(TestCase):
  def setUp(self) -> None:
    logging.basicConfig(level=logging.DEBUG)
    self.user = User.objects.get_or_create(username='testuser')[0]

  async def __create_communicator_and_connect(self) -> MessageWebsocketCommunicator:
    communicator = MessageWebsocketCommunicator(application, "ws/")
    communicator.scope['user'] = self.user
    connected, _ = await communicator.connect()
    self.assertTrue(connected, "Could not connect.")
    return communicator
  
  async def __assert_reception_of_reviews_done(self):
    message, _ = await communicator.receive_message_from()
    self.assertEqual(message, "reviews_done")
  
  async def __test_no_pending_reviews(self):
    """
    Disconnect with reviews_done when no reviews are pending.
    """

    communicator = await self.__create_communicator_and_connect()
    await communicator.send_message_to('start_reviews')
    await self.__assert_reception_of_reviews_done()

    await communicator.disconnect()
    await communicator.wait()

  async def test_complete(self):
    """
    Succesfully complete an SRS session in which the user answers all cards.
    """
    ENTRY_COUNT = 5
    EXPIRED_ENTRY_COUNT = 3

    @database_sync_to_async
    def create_flashcards():
      update_db_from_jmd(jmdict.Jmdict([
        jmdict.Entry(
          i,
          k_ele=[], 
          r_ele=[jmdict.REle(f'test{i}', [], [])],
          sense=[]
        ) 
        for i in range(ENTRY_COUNT) 
      ]))

      flashcards = (Flashcard(
        owner=self.user,
        entry=entry,
        leitner_box=0,
        expiration_timestamp=timezone.now() - timedelta(days=1 if i < EXPIRED_ENTRY_COUNT else -1),
        last_review_date=timezone.now() - timedelta(days=30)
      ) for i, entry in enumerate(Entry.objects.all()))

      Flashcard.objects.bulk_create(flashcards)

    await create_flashcards()

    communicator = await self.__create_communicator_and_connect()
    await communicator.send_message_to('start_reviews')
    for _ in range(EXPIRED_ENTRY_COUNT):
      message, _ = await communicator.receive_message_from()
      self.assertEqual(message, 'new_card')
      await communicator.send_message_to('answer', confidence=2)
    
    self.__assert_reception_of_reviews_done()

    await communicator.disconnect()
    await communicator.wait()