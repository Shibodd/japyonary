from srs.consumers.srs_consumer import SrsConsumer, SrsReviewState
from types import SimpleNamespace

from django.test import TestCase
from unittest.mock import patch, AsyncMock, Mock

@patch.object(SrsConsumer, 'panic')
@patch.object(SrsConsumer, 'send_message')
@patch.object(SrsConsumer, 'close')
@patch.object(SrsConsumer, 'accept')
class TestSrsConsumer(TestCase):
  async def test_user_not_authenticated(self, mock_accept, mock_close, mock_send_message, mock_panic):
    """ If the user is not authenticated, the connection should be immediately closed with panic. """

    consumer = SrsConsumer()
    consumer.scope = { 'user': SimpleNamespace(is_authenticated = False) }

    await consumer.connect()
    mock_accept.assert_awaited_once()
    mock_panic.assert_awaited_once()