from srs.consumers.srs_consumer import SrsConsumer, SrsException, AsyncMessageDispatchingWebsocketConsumer
from types import SimpleNamespace

from django.test import TestCase
from unittest.mock import patch, AsyncMock, Mock

@patch.object(SrsConsumer, 'send_message', new=Mock())
@patch.object(SrsConsumer, 'panic')
@patch.object(SrsConsumer, 'close')
@patch.object(SrsConsumer, 'accept')
@patch('srs.consumers.srs_consumer.SrsReview', autospec=True)
class TestSrsConsumer(TestCase):

  # Helpers
  def __create_consumer_with_user_auth(is_authenticated):
    consumer = SrsConsumer()
    consumer.scope = { 'user': SimpleNamespace(is_authenticated = is_authenticated) }
    return consumer
  
  async def __create_and_connect_consumer_with_asserts(self, mock_accept, mock_close, mock_review_init):
    consumer = TestSrsConsumer.__create_consumer_with_user_auth(True)
    await consumer.connect()
    mock_accept.assert_awaited_once()
    mock_close.assert_not_called()
    mock_review_init.assert_not_called()
    return consumer


  # Tests
  async def test_user_not_authenticated(self, mock_review_init, mock_accept, mock_close, mock_panic):
    """
    If the user is not authenticated, SrsConsumer should immediately disconnect.
    SrsReview should not be used.
    """
    consumer = TestSrsConsumer.__create_consumer_with_user_auth(False)

    await consumer.connect()
    mock_accept.assert_not_called()
    mock_close.assert_awaited()
    mock_review_init.assert_not_called()

  async def test_user_authenticated(self, mock_review_init, mock_accept, mock_close, mock_panic):
    """
    If the user is authenticated, then the connection should be accepted.
    The consumer should then not perform any other action until
    the client sends the start message.
    """
    await self.__create_and_connect_consumer_with_asserts(mock_accept, mock_close, mock_review_init)

  @patch.object(AsyncMessageDispatchingWebsocketConsumer, 'receive_message')
  async def test_panic_on_srs_exception(self, mock_super_receive_message, mock_review_init, mock_accept, mock_close, mock_panic):
    """
    If an SrsException is raised by SrsReview, the consumer should panic.
    """
    consumer = await self.__create_and_connect_consumer_with_asserts(mock_accept, mock_close, mock_review_init)
    
    # This would normally dispatch the calls to the appropriate SrsReview method.
    mock_super_receive_message.side_effect = SrsException("Test exception")

    await consumer.receive_message('test_message')
    mock_panic.assert_awaited_once()