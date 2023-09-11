from typing import Tuple
from django.test import TestCase
from srs.models import Flashcard, FlashcardSnapshot
from srs.review import SrsBridge, SrsException, SrsReview
import logging
from users.models import User
from unittest.mock import patch, call, AsyncMock

from srs.tests.generate_flashcards import generate_flashcards

class SrsReviewTests(TestCase):
  def setUp(self) -> None:
    self.user = User.objects.get_or_create(username='testuser')[0]

  async def test_with_no_pending_reviews(self):
    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)

    await review.start(self.user)
    mock_bridge.srs_new_card.assert_not_called()
    mock_bridge.srs_reviews_done.assert_awaited_once()

  async def test_answer_all_pending_reviews(self):
    PENDING_REVIEWS = 3
    await generate_flashcards(self.user, PENDING_REVIEWS, 2)

    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)

    await review.start(self.user)
    mock_bridge.srs_new_card.assert_awaited_once()
    mock_bridge.srs_reviews_done.assert_not_called()
    mock_bridge.reset_mock()

    for i in range(PENDING_REVIEWS - 1):
      await review.answer(1)
      mock_bridge.srs_new_card.assert_awaited_once()
      mock_bridge.srs_reviews_done.assert_not_called()
      mock_bridge.reset_mock()

    await review.answer(1)
    mock_bridge.srs_new_card.assert_not_called()
    mock_bridge.srs_reviews_done.assert_awaited_once()

  async def test_no_available_undos(self):
    """
    SrsReview should correctly announce undo is not available,
    and raise an SrsException when an Undo is attempted when there are no available undos.
    """
    await generate_flashcards(self.user, 1)
    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)
    await review.start(self.user)

    self.assertEqual(mock_bridge.srs_new_card.mock_calls[0].args[1], False, 'SrsReview announces that an undo is available.')

    with self.assertRaises(SrsException):
      await review.undo()
  
  async def test_undo_order(self):
    """ Undo should display cards in the same order the user first answered them. """
    UNDO_COUNT = 2
    await generate_flashcards(self.user, UNDO_COUNT + 1)
    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)
    
    html_stack = []

    def get_last_card_html():
      mock_bridge.srs_new_card.assert_awaited_once()
      ans = mock_bridge.srs_new_card.mock_calls[0].args[0]
      mock_bridge.srs_new_card.reset_mock()
      return ans

    await review.start(self.user)
    html_stack.append(get_last_card_html())

    for i in range(UNDO_COUNT):
      await review.answer(1)
      html_stack.append(get_last_card_html())

    # We didn't answer the last one, but we still pushed its html on the stack
    html_stack.pop()
    
    for i in range(UNDO_COUNT):
      await review.undo()
      self.assertHTMLEqual(get_last_card_html(), html_stack.pop())

    for i in range(UNDO_COUNT + 1):
      await review.answer(1)

    mock_bridge.srs_reviews_done.assert_awaited_once()

  async def __single_flashcard_get_old_new(self, review, mock_bridge, answer) -> Tuple[FlashcardSnapshot, FlashcardSnapshot]:
    old = (await Flashcard.objects.aget()).get_snapshot()

    await review.start(self.user)
    mock_bridge.srs_new_card.assert_awaited_once()
    mock_bridge.srs_reviews_done.assert_not_called()
    
    await review.answer(answer)
    mock_bridge.srs_reviews_done.assert_awaited_once()

    new = (await Flashcard.objects.aget()).get_snapshot()
    return old, new
  
  async def test_positive_answer_updates(self):
    """ A positive answer should correctly update a flashcard. """

    await generate_flashcards(self.user, 1)
    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)

    old, new = await self.__single_flashcard_get_old_new(review, mock_bridge, answer = 1)
    self.assertGreater(new.expiration_date, old.expiration_date)
    self.assertGreater(new.last_review_timestamp, old.last_review_timestamp)
    self.assertGreater(new.leitner_box, old.leitner_box)

  async def test_bad_answer_updates(self):
    """ Answer should correctly update a flashcard. """

    await generate_flashcards(self.user, 1)
    flashcard = await Flashcard.objects.aget()
    flashcard.leitner_box = 5
    await flashcard.asave()

    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)

    old, new = await self.__single_flashcard_get_old_new(review, mock_bridge, answer = 0)
    self.assertGreater(new.expiration_date, old.expiration_date)
    self.assertGreater(new.last_review_timestamp, old.last_review_timestamp)
    self.assertLess(new.leitner_box, old.leitner_box)


  async def test_undo_restores_flashcard(self):
    """ Undo should correctly restore a flashcard. """
    await generate_flashcards(self.user, 2)

    mock_bridge = AsyncMock(spec=SrsBridge)
    review = SrsReview(mock_bridge)

    async def snapshot_flashcards():
      return { x.pk: x.get_snapshot() async for x in Flashcard.objects.all() }

    old = await snapshot_flashcards()

    await review.start(self.user)
    mock_bridge.srs_new_card.assert_awaited_once()
    mock_bridge.srs_new_card.reset_mock()

    await review.answer(1)
    mock_bridge.srs_new_card.assert_awaited_once()
    mock_bridge.srs_new_card.reset_mock()

    after_answer = await snapshot_flashcards()
    self.assertNotEqual(old, after_answer, "Answer did not modify the flashcard.")

    await review.undo()
    mock_bridge.srs_new_card.assert_awaited_once()
    mock_bridge.srs_new_card.reset_mock()

    after_undo = await snapshot_flashcards()
    self.assertNotEqual(after_answer, after_undo, "The undo did not modify the flashcard.")
    self.assertEqual(old, after_undo, "Undo modified the flashcard to the wrong state.")