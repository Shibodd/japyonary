from typing import Any, Optional
from django.db import models
from django.views.generic import DeleteView
from decks.models import Deck
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class DeckDeleteView(LoginRequiredMixin, DeleteView):
  model = Deck
  slug_field = 'id'
  success_url = reverse_lazy('decks:deck_search')

  def get_object(self, queryset = None):
    obj = super().get_object(queryset)
    if obj.owner != self.request.user:
      raise PermissionDenied("You can't delete other users decks.")
    return obj