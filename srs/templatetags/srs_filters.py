from django import template
from dictionary.models import Entry
from srs.models import Flashcard
from users.models import User

register = template.Library()

@register.filter
def is_in_user_srs(entry: Entry, user: User):
  return Flashcard.objects.filter(owner=user, entry=entry).exists()