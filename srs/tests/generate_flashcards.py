from channels.db import database_sync_to_async
from dictionary.management.commands import jmdict_xml
from dictionary.models import Entry
from srs.models import Flashcard
from django.utils import timezone
from datetime import timedelta
from dictionary.management.commands.load_dictionary import update_db as update_db_from_jmd

@database_sync_to_async
def generate_flashcards(user, expired_entry_count, additional_entry_count=0):
  update_db_from_jmd(jmdict_xml.Jmdict([
    jmdict_xml.Entry(
      i,
      k_ele=[], 
      r_ele=[jmdict_xml.REle(f'test_entry{i}', [], [])],
      sense=[]
    ) 
    for i in range(expired_entry_count + additional_entry_count) 
  ]))

  now = timezone.now()
  today = now.date()

  flashcards = (Flashcard(
    owner=user,
    entry=entry,
    leitner_box=0,
    expiration_date=today - timedelta(days=1 if i < expired_entry_count else -1),
    last_review_timestamp=now - timedelta(days=30)
  ) for i, entry in enumerate(Entry.objects.all()))

  Flashcard.objects.bulk_create(flashcards)