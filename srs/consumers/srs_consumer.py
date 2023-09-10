from srs.consumers.message_consumer import MessageWebsocketConsumer
from srs.review import SrsException, SrsReview, SrsBridge
import functools

class SrsConsumer(MessageWebsocketConsumer, SrsBridge):
  review = functools.cached_property(SrsReview)


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


  # Helpers for message handlers
  def panic_on_srs_exceptions(fn):
    @functools.wraps(fn)
    async def wrapper(self):
      try:
        await fn()
      except SrsException as e:
        await self.panic(e.args.join(' '))
    return wrapper


  # Message handlers
  @panic_on_srs_exceptions
  async def handle_start_reviews(self):
    await self.review.start(self.scope['user'])

  @panic_on_srs_exceptions
  async def handle_answer(self):
    await self.review.answer()

  @panic_on_srs_exceptions
  async def handle_undo(self):
    await self.review.undo()

  message_handlers = {
    'start_reviews': handle_start_reviews,
    'answer': handle_answer,
    'undo': handle_undo,
  }