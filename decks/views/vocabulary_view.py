from typing import Any, Dict
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from dictionary.models import Entry
from decks.models import Deck
from django import http
from django.shortcuts import redirect

from dictionary.views import DictionarySearchView
from django.core.exceptions import BadRequest
from decks.forms import ImportVocabFromFileForm
from dictionary import vocab_parsing

class DeckVocabularyView(DictionarySearchView):
  template_name = 'decks/deck_vocabulary.html'

  def fill_deck_field(self, slug):
    self.deck = Deck.objects.filter(pk = slug).first()
    if self.deck is None:
      raise BadRequest("Deck does not exist.")

  def post(self, request: HttpRequest, slug, *args, **kwargs):
    self.fill_deck_field(slug)

    file = request.FILES.get('uploaded_vocabulary_file')
    if not file:
      raise BadRequest("No file provided for uplod.")
    
    entry_ids = vocab_parsing.get_entries_from_file(file)

    Deck.dictionary_entries.through.objects.bulk_create(
      (Deck.dictionary_entries.through(deck_id = slug, entry_id=entry_id) for entry_id in entry_ids),
      ignore_conflicts = True
    )

    return redirect('decks:deck_vocabulary', slug=self.deck.pk)


  def get(self, request: HttpRequest, slug, *args, **kwargs):
    self.fill_deck_field(slug)
    
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
      'deck_edit_mode': self.deck_edit_mode,
      'import_vocab_from_file_form': ImportVocabFromFileForm(self.deck.pk)
    })
    return ctx

  def get_base_queryset(self) -> QuerySet[Entry]:
    if self.deck is None:
      return http.HttpResponseBadRequest("Invalid request")
    
    if self.deck_edit_mode:
      return Entry.objects.all()
    else:
      return self.deck.dictionary_entries.all()