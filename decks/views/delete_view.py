from django.views.generic import DeleteView
from decks.models import Deck
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from decks.views.mixins import DeckEditPermissionTestMixin
from japyonary import utils

class DeckDeleteView(LoginRequiredMixin, DeckEditPermissionTestMixin, utils.StatusBarFormValidationMixin, DeleteView):
  model = Deck
  slug_field = 'id'
  success_url = reverse_lazy('decks:deck_search')
  status_bar_message_on_success = "Deck deleted successfully."