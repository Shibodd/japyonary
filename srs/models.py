from django.db import models
from dictionary.models import Entry
from users.models import User

class Flashcard(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE)
  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)

  leitner_box = models.IntegerField()
  expiration_timestamp = models.DateTimeField()
  last_review_date = models.DateTimeField()

  class Meta:
    constraints = (models.UniqueConstraint('entry', 'owner', name='user_one_flashcard_per_entry'), )