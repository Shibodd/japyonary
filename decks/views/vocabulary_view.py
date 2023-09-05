from typing import Any, Dict
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from dictionary.models import Entry
from decks.models import Deck
from django import http

from dictionary.views import DictionarySearchView
from django.core.exceptions import BadRequest

def mandatory(obj):
  if obj is None:
    raise BadRequest()
  return obj

class DeckVocabularyView(DictionarySearchView):
  template_name = 'decks/deck_vocabulary.html'

  def get(self, request: HttpRequest, *args, **kwargs):
    self.deck = Deck.objects.get(
      pk = mandatory(self.request.resolver_match.kwargs.get('slug'))
    )
    
    self.deck_edit_mode = \
      request.resolver_match.url_name == 'deck_vocabulary_edit' \
      and request.user.is_authenticated \
      and self.deck.owner == request.user
    
    self.show_all_with_no_query = not self.deck_edit_mode
    
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)
    ctx.update({
      'deck': self.deck,
      'deck_edit_mode': self.deck_edit_mode
    })
    return ctx

  def get_base_queryset(self) -> QuerySet[Entry]:
    if self.deck is None:
      return http.HttpResponseBadRequest("Invalid request")
    
    if self.deck_edit_mode:
      return Entry.objects.all()
    else:
      return self.deck.dictionary_entries.all()