from django import template
from decks.models import Deck
from users.models import User
register = template.Library()

@register.filter
def is_hearted_by(deck: Deck, user: User):
  return deck.is_hearted_by(user)