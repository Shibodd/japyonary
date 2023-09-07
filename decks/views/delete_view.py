from django.views.generic import DeleteView
from decks.models import Deck
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from decks.views.mixins import DeckEditPermissionTestMixin

class DeckDeleteView(LoginRequiredMixin, DeckEditPermissionTestMixin, DeleteView):
  model = Deck
  slug_field = 'id'
  success_url = reverse_lazy('decks:deck_search')