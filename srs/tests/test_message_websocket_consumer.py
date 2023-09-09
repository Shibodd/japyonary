from django.test import TestCase
from srs.consumers.message_consumer import MessageWebsocketConsumer

from unittest.mock import patch, AsyncMock

@patch.object(MessageWebsocketConsumer, 'send_json')
@patch.object(MessageWebsocketConsumer, 'close')
@patch.object(MessageWebsocketConsumer, 'test_handler1', create=True, new_callable=AsyncMock)
@patch.object(MessageWebsocketConsumer, 'test_handler2', create=True, new_callable=AsyncMock)
class MessageWebsocketConsumerTests(TestCase):

  async def test_dispatch_succeeds(self, mock_test_handler2, mock_test_handler1, mock_close, mock_send_json):
    """ The dispatcher should, upon receival of an handled message, await the correct handler and then keep the connection open. """

    consumer = MessageWebsocketConsumer()

    payload1 = { 'testValue': 123 }
    payload2 = { 'myValue': 321 }

    handlers = {
      'first': consumer.test_handler1,
      'second': consumer.test_handler2
    }

    with patch.dict(consumer.message_handlers, handlers):
      await consumer.receive_json({
        'message': 'first',
        'payload': payload1
      })
      mock_test_handler1.assert_awaited_once_with(consumer, payload1)
      mock_test_handler1.reset_mock()
      
      await consumer.receive_json({
        'message': 'second',
        'payload': payload2
      })
      mock_test_handler2.assert_awaited_once_with(consumer, payload2)
      mock_test_handler1.assert_not_called() # Handler1 shouldn't have been called again
    
    mock_close.assert_not_called()
    mock_send_json.assert_not_called()


  async def test_dispatch_fails(self, mock_test_handler2, mock_test_handler, mock_close, mock_send_json):
    """ The dispatcher should, upon receival of an unhandled message, close the connection and send some error message. """

    consumer = MessageWebsocketConsumer()

    with patch.dict(consumer.message_handlers, { 'test_message': consumer.test_handler1 }):
      await consumer.receive_json({
        'message': 'bogus_message',
        'payload': 123
      })
    
    mock_test_handler.assert_not_called()
    mock_close.assert_awaited()
    mock_send_json.assert_awaited_once()

    self.assertDictContainsSubset({ 'message': 'panic' }, mock_send_json.call_args_list[0].args[0])