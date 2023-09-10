from django.test import TestCase
from channels.testing import WebsocketCommunicator
from users.models import User
from channels.db import database_sync_to_async

from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from srs.consumers import SrsConsumer
from django.urls import path
import logging

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
  
  async def test_no_pending_reviews(self):
    """
    Disconnect with reviews_done when no reviews are pending.
    """

    communicator = await self.__create_communicator_and_connect()
    await communicator.send_message_to('start_reviews')
    message, _ = await communicator.receive_message_from()

    self.assertEqual(message, "reviews_done")

    await communicator.disconnect()
    await communicator.wait()

    
  