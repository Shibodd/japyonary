from django.core.exceptions import PermissionDenied

class DeckEditPermissionTestMixin():
  def get_object(self, queryset = None):
    deck = super().get_object(queryset)

    ok = deck.owner == self.request.user or self.request.user.is_superuser
    if ok:
      return deck
    raise PermissionDenied("Cannot modify other users deck.")
  
class DeckViewPermissionTestMixin():
  def get_object(self, queryset = None):
    deck = super().get_object(queryset)

    ok = not deck.is_private or self.request.user == deck.owner or self.request.user.is_superuser
    if ok:
      return deck
    raise PermissionDenied("Cannot view private decks.")