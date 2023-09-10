from django.db import models
from dictionary.models import Entry
from users.models import User


class FlashcardQuerySet(models.QuerySet):
  def expired(self, user, now):
    return self \
      .filter(models.Q(owner=user) & models.Q(expiration_timestamp__lt=now)) \
      .order_by('expiration_timestamp')
    
class Flashcard(models.Model):
  objects = models.Manager.from_queryset(FlashcardQuerySet)()
  objects: FlashcardQuerySet

  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

  leitner_box = models.IntegerField()
  expiration_timestamp = models.DateTimeField()
  last_review_date = models.DateTimeField()

  class Meta:
    constraints = (models.UniqueConstraint('entry', 'owner', name='user_one_flashcard_per_entry'), )