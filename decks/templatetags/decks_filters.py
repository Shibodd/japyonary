from django import template
from dictionary.models import Entry
from decks.models import Deck
from users.models import User
register = template.Library()

@register.filter
def is_hearted_by(deck: Deck, user: User):
  return deck.is_hearted_by(user)

@register.filter
def deck_contains_entry(deck: Deck, entry: Entry):
  return deck.dictionary_entries.contains(entry)