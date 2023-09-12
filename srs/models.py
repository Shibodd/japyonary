from django.db import models
from dictionary.models import Entry
from users.models import User
from dataclasses import dataclass
from datetime import datetime, date


class FlashcardQuerySet(models.QuerySet):
  def expired(self, user, now: datetime):
    return self \
      .filter(models.Q(owner=user) & models.Q(expiration_date__lte=now.date())) \
      .order_by('expiration_date')
  
  def prefetch_everything(self):
    return self.select_related('entry')

@dataclass
class FlashcardSnapshot:
  flashcard_pk: object
  leitner_box: int
  expiration_date: date
  last_review_timestamp: datetime

class Flashcard(models.Model):
  objects = models.Manager.from_queryset(FlashcardQuerySet)()
  objects: FlashcardQuerySet

  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

  leitner_box = models.IntegerField(default=0)
  expiration_date = models.DateField(default=date.min, null=False)
  last_review_timestamp = models.DateTimeField(null=True)

  def get_snapshot(self) -> FlashcardSnapshot:
    return FlashcardSnapshot(
      self.pk,
      self.leitner_box,
      self.expiration_date,
      self.last_review_timestamp
    )

  def __str__(self) -> str:
    return f"{self.owner.username} - {self.entry.ent_seq}"


  class Meta:
    constraints = (models.UniqueConstraint('entry', 'owner', name='user_one_flashcard_per_entry'), )