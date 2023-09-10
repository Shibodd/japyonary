from django.test import TestCase
from srs.consumers import AsyncMessageDispatchingWebsocketConsumer

from unittest.mock import patch, AsyncMock

@patch.object(AsyncMessageDispatchingWebsocketConsumer, 'panic')
@patch.object(AsyncMessageDispatchingWebsocketConsumer, 'message_handlers',
              new_callable=lambda: dict({ 'first': AsyncMock(), 'second': AsyncMock() }))
class MessageWebsocketConsumerTests(TestCase):

  async def test_dispatches_to_correct_method(self, mock_message_handlers, mock_panic):
    """
    The dispatcher should,
    upon receival of an handled message,
    await the correct handler and then keep the connection open.
    """

    PAYLOAD = { 'testValue': 123 }
    consumer = AsyncMessageDispatchingWebsocketConsumer()

    await consumer.receive_message('first', **PAYLOAD)
    mock_message_handlers['first'].assert_awaited_once_with(consumer, **PAYLOAD)
    mock_message_handlers['second'].assert_not_called()
    mock_message_handlers['first'].reset_mock()

    await consumer.receive_message('second', **PAYLOAD)
    mock_message_handlers['second'].assert_awaited_once_with(consumer, **PAYLOAD)
    mock_message_handlers['first'].assert_not_called() # Handler1 shouldn't have been called again

    mock_panic.assert_not_called()


  async def test_dispatch_fails(self, mock_message_handlers, mock_panic):
    """
    The dispatcher should,
    upon receival of an unhandled message, 
    close the connection and send some error message without calling any handler.
    """

    consumer = AsyncMessageDispatchingWebsocketConsumer()

    await consumer.receive_message('bogus_message', bogus_field=3)
    mock_panic.assert_awaited_once()

    for handler in mock_message_handlers.values():
      handler.assert_not_called()
    