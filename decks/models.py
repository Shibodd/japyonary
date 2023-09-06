from django.db import models
from users.models import User
from dictionary.models import Entry

class DeckQuerySet(models.QuerySet):
  def top(self):
    return self \
    .annotate(heart_count=models.Count('hearts')) \
    .order_by('-heart_count')
  
# Create your models here.
class Deck(models.Model):
  objects = models.Manager.from_queryset(DeckQuerySet)()

  owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='owned_decks')
  dictionary_entries = models.ManyToManyField(Entry)
  hearts = models.ManyToManyField(User, related_name='hearted_decks', blank=True)

  name = models.CharField(max_length=64, null=False, blank=False)
  description = models.TextField(blank=True, null=True)
  is_private = models.BooleanField(null=False, default=True)
  cover_image = models.ImageField(upload_to='deck_cover_images', blank=True)

  def is_hearted_by(self, user: User):
    return self.hearts.contains(user)

class Comment(models.Model):
  deck = models.ForeignKey(Deck, on_delete=models.CASCADE, null=False)
  owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  text = models.TextField(blank=False, null=False)
  creation_timestamp = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    get_latest_by = 'creation_timestamp'