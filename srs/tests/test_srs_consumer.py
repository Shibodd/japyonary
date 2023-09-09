from srs.consumers.srs_consumer import SrsConsumer, SrsReviewState
from types import SimpleNamespace

from django.test import TestCase
from unittest.mock import patch, AsyncMock, Mock

def get_path(klass):
  return f'{klass.__module__}.{klass.__qualname__}'

@patch.object(SrsConsumer, 'panic')
@patch.object(SrsConsumer, 'send_message')
@patch.object(SrsConsumer, 'close')
@patch.object(SrsConsumer, 'accept')
@patch.object(SrsConsumer, 'scope', new={ 'user': SimpleNamespace(is_authenticated = True) }, create=True)
@patch(get_path(SrsReviewState), autospec=True)

class TestSrsConsumer(TestCase):
  async def test_user_not_authenticated(self, mock_review_state_init, mock_accept, mock_close, mock_send_message, mock_panic):
    """
    If the user is not authenticated, SrsConsumer should panic on connect.
    SrsState should not be used, either (avoid accessing the DB for no reason)
    """

    consumer = SrsConsumer()
    consumer.scope['user'].is_authenticated = False

    await consumer.connect()
    mock_accept.assert_awaited_once()
    mock_panic.assert_awaited_once()
    mock_review_state_init.assert_not_called()
  
  async def test_no_pending_reviews(self, mock_review_state_init, mock_accept, mock_close, mock_send_message, mock_panic):
    """ If connecting when no reviews are pending, SrsConsumer should send the reviews_done message and disconnect. """

    consumer = SrsConsumer()
    mock_review_state = mock_review_state_init.return_value
    mock_review_state.user.return_value = consumer.scope['user']
    mock_review_state.get_current_entry.return_value = None

    await consumer.connect()

    print(consumer.assert_has_calls)

    mock_accept.assert_awaited_once()
    mock_send_message.assert_awaited_once_with('reviews_done')
    mock_close.assert_awaited_once()

  