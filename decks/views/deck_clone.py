from django.views.generic import View
from django.core.exceptions import BadRequest, PermissionDenied
from decks.models import Deck
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from japyonary import utils

class DeckCloneView(LoginRequiredMixin, View):
  def post(self, request):
    deck_id = request.POST.get('deck_id')
    if not deck_id:
      raise BadRequest('Missing deck_id.')

    deck = Deck.objects.get(pk = deck_id)
    if not deck:
      raise BadRequest('Deck not found.')
    
    if deck.is_private and deck.owner != request.user:
      raise PermissionDenied('This deck is private.')
    
    old_entries = deck.dictionary_entries.all()

    deck.pk = None
    deck.name = f"Copy of {deck.name} by {deck.owner.username}"
    deck.owner = request.user
    deck.save()
    deck.dictionary_entries.set(old_entries)
    
    utils.add_statusbar_message(self.request, "Deck cloned successfully.")
    return redirect('decks:deck_detail', slug = deck.pk)