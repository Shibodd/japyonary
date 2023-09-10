class SrsReview():
  _review_in_progress = False
  review_in_progress = property(lambda self: self._review_in_progress)

  _user = None
  user = property(lambda self: self._user)

  async def start(self, user):
    self._user = user
    self._review_in_progress = True
  
  async def stop(self):
    pass

  async def answer(self, confidence):
    pass

  async def undo(self):
    pass

  def get_current_entry(self) -> Entry:
    pass


class SrsException(Exception):
  pass

from abc import ABC
class SrsBridge(ABC):
  async def srs_new_card(self, html):
    pass
  async def srs_reviews_done(self):
    pass

"""
def __review_in_progress_required(in_progress=True):
  def decorator(fn):
    @functools.wraps(fn)
    async def wrapper(self):
      if self.review.review_in_progress == in_progress:
        await fn()
      else:
        await self.panic('Protocol error')
    return wrapper
  return decorator
"""