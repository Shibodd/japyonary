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
from srs.tests.generate_flashcards import generate_flashcards

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
    self.user = User.objects.get_or_create(username='testuser')[0]

  async def __create_communicator_and_connect(self) -> MessageWebsocketCommunicator:
    communicator = MessageWebsocketCommunicator(application, "ws/")
    communicator.scope['user'] = self.user
    connected, _ = await communicator.connect()
    self.assertTrue(connected, "Could not connect.")
    return communicator
  
  async def __assert_reception_of_reviews_done(self, communicator):
    message, _ = await communicator.receive_message_from()
    self.assertEqual(message, "reviews_done")
  
  async def test_no_pending_reviews(self):
    """
    Disconnect with reviews_done when no reviews are pending.
    """

    communicator = await self.__create_communicator_and_connect()
    await communicator.send_message_to('start_reviews')
    await self.__assert_reception_of_reviews_done(communicator)

    await communicator.disconnect()
    await communicator.wait()

  async def test_complete(self):
    """
    Succesfully complete an SRS session in which the user answers all cards.
    """
    EXPIRED_ENTRY_COUNT = 3
    await generate_flashcards(self.user, EXPIRED_ENTRY_COUNT, 2)

    communicator = await self.__create_communicator_and_connect()
    await communicator.send_message_to('start_reviews')
    for _ in range(EXPIRED_ENTRY_COUNT):
      message, _ = await communicator.receive_message_from()
      self.assertEqual(message, 'new_card')
      
      await communicator.send_message_to('answer', confidence=2)

    await self.__assert_reception_of_reviews_done(communicator)

    await communicator.disconnect()
    await communicator.wait()