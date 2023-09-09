from srs.consumers.message_consumer import MessageWebsocketConsumer
from django.template.loader import render_to_string

from dictionary.models import Entry
from srs.models import Flashcard

class SrsReviewState():
  def __init__(self, user):
    self._user = user

  async def start(self):
    pass

  async def answer(self, confidence):
    pass

  async def undo(self):
    pass

  def get_current_entry(self) -> Entry:
    pass

  @property
  def user(self):
    return self._user

class SrsConsumer(MessageWebsocketConsumer):
  async def update_client(self):
    entry = self.review_state.get_current_entry()

    if not entry:
      await self.send_message('reviews_done')
      await self.close()
    else:
      html = render_to_string('srs/card.html', context = {
        'entry': entry,
        'user': self.review_state.user
      })
      self.send_message('new_card', html=html)
      

  async def connect(self):
    await self.accept()

    user = self.scope['user']
    if not user.is_authenticated:
      return await self.panic('User is not logged in')

    self.review_state = SrsReviewState(user)
    await self.review_state.start()
    await self.update_client()


  async def answer(self, payload):
    confidence = payload.get('confidence')
    if confidence is None:
      return await self.panic('Bad payload')
    
    await self.review_state.answer(confidence)
    await self.update_client()


  async def undo(self, payload):
    await self.review_state.undo()
    await self.update_client()


  message_handlers = {
    'answer': answer,
    'undo': undo
  }

  async def disconnect(self, close_code):
    pass