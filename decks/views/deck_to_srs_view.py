from django.views import View
from django.http import HttpRequest, Http404
from django.core.exceptions import BadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from japyonary.utils import add_statusbar_message

from srs.models import Flashcard
from decks.models import Deck

class DeckToSrsView(LoginRequiredMixin, View):
  def post(self, request: HttpRequest):
    deck_id = request.POST.get('deck_id')
    if deck_id is None:
      raise BadRequest("Missing deck id")
    
    deck = Deck.objects.filter(pk=deck_id).first()
    if deck is None:
      return Http404("The deck does not exist.")
    
    Flashcard.objects.bulk_create(
      (Flashcard(owner=request.user, entry=entry) for entry in deck.dictionary_entries.all()),
      ignore_conflicts=True
    )

    add_statusbar_message(self.request, "Succesfully added all entries to the SRS.")
    return redirect('decks:deck_vocabulary', deck_id)