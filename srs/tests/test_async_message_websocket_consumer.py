from django.test import TestCase
from srs.consumers import AsyncMessageWebsocketConsumer

from unittest.mock import patch

class MessageWebsocketConsumerTests(TestCase):
  @patch.object(AsyncMessageWebsocketConsumer, 'send_json')
  @patch.object(AsyncMessageWebsocketConsumer, 'close')
  async def test_panic_disconnects(self, mock_close, mock_send_json):
    """ Panic should result in a 'panic' message sent and a disconnection. """

    REASON = 'test_message'

    consumer = AsyncMessageWebsocketConsumer()
    await consumer.panic(REASON)
    mock_send_json.assert_awaited_once_with({
      'message': 'panic',
      'payload': {
        'reason': REASON
      }
    })
    mock_close.assert_awaited_once()

  @patch.object(AsyncMessageWebsocketConsumer, 'panic')
  async def test_no_message_field(self, mock_panic):
    """
    Reception of JSON content without the message field
    should result in panic being called.
    """

    consumer = AsyncMessageWebsocketConsumer()
    await consumer.receive_json({
      'hello': 'world',
      'payload': { 'foo': 'bar' }
    })
    mock_panic.assert_awaited_once()
    

  @patch.object(AsyncMessageWebsocketConsumer, 'panic')
  @patch.object(AsyncMessageWebsocketConsumer, 'receive_message')
  async def test_no_payload_field(self, mock_receive_message, mock_panic):
    """
    Reception of JSON content without the payload field is valid, and
    should result in a call to receive_message with no kwargs.
    """

    MESSAGE = 'test'

    consumer = AsyncMessageWebsocketConsumer()
    await consumer.receive_json({
      'message': MESSAGE,
      'foo': 'bar'
    })

    mock_panic.assert_not_called()
    mock_receive_message.assert_awaited_with(MESSAGE)

  @patch.object(AsyncMessageWebsocketConsumer, 'panic')
  @patch.object(AsyncMessageWebsocketConsumer, 'receive_message')
  async def test_complete(self, mock_receive_message, mock_panic):
    """
    Reception of JSON content representing a complete and valid message
    should result in a complete call to receive_message.
    """

    MESSAGE = 'test'
    PAYLOAD = {
      'my_field': 'my_value',
      '123': '321'
    }

    consumer = AsyncMessageWebsocketConsumer()
    await consumer.receive_json({
      'message': MESSAGE,
      'payload': PAYLOAD,
      'foo': 'bar'
    })

    mock_panic.assert_not_called()
    mock_receive_message.assert_awaited_with(MESSAGE, **PAYLOAD)