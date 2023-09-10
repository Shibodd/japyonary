from srs.consumers import AsyncMessageDispatchingWebsocketConsumer
from srs.review import SrsException, SrsReview, SrsBridge
import logging
import functools

class SrsConsumer(AsyncMessageDispatchingWebsocketConsumer, SrsBridge):
  logger = logging.getLogger(__name__)
  review = functools.cached_property(lambda self: SrsReview(self))

  # Bridge implementation
  async def srs_new_card(self, html):
    await self.send_message('new_card', html=html)
  
  async def srs_reviews_done(self):
    await self.send_message('reviews_done')
    await self.close()


  # Websocket connection
  async def connect(self):
    self.user = self.scope['user']
    if not self.user.is_authenticated:
      self.logger.info("Refused an unauthenticated connection.")
      await self.close()
    else:
      self.logger.info('Accepting connection from user "%s".', self.user.username)
      await self.accept()

  async def disconnect(self, code):
    await self.review.stop()


  # Message handlers
  async def receive_message(self, message, **payload):
    try:
      await super().receive_message(message, **payload)
    except SrsException as e:
      exc_msg = " ".join(e.args)
      self.logger.info('User "%s" triggered an SrsException: %s', self.user.username, exc_msg)
      await self.panic(exc_msg)

  async def handle_start_reviews(self, **payload):
    await self.review.start(self.user)

  async def handle_answer(self, **payload):
    confidence = payload.get('confidence')
    if confidence is None:
      self.logger.info('User "%s" sent an invalid "answer" message.', self.user.username)
      await self.panic('SRS protocol error')
    else:
      await self.review.answer()

  async def handle_undo(self, **payload):
    await self.review.undo()

  message_handlers = {
    'start_reviews': handle_start_reviews,
    'answer': handle_answer,
    'undo': handle_undo
  }