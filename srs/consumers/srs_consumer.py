from srs.consumers import AsyncMessageDispatchingWebsocketConsumer
from srs.review import SrsException, SrsReview, SrsBridge
import functools

class SrsConsumer(AsyncMessageDispatchingWebsocketConsumer, SrsBridge):
  review = functools.cached_property(lambda self: SrsReview(self))

  # Bridge implementation
  async def srs_new_card(self, html):
    await self.send_message('new_card', html=html)
  
  async def srs_reviews_done(self):
    await self.send_message('reviews_done')
    await self.close()


  # Websocket connection
  async def connect(self):
    if not self.scope['user'].is_authenticated:
      await self.close()
    else:
      await self.accept()

  async def disconnect(self, code):
    await self.review.stop()


  # Message handlers
  async def receive_message(self, message, **payload):
    try:
      await super().receive_message(message, **payload)
    except SrsException as e:
      await self.panic(" ".join(e.args))

  async def handle_start_reviews(self, **payload):
    await self.review.start(self.scope['user'])

  async def handle_answer(self, **payload):
    confidence = payload.get('confidence')
    if confidence is None:
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