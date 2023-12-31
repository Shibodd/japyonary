from django.db import models
from users.models import User
from dictionary.models import Entry


class DeckQuerySet(models.QuerySet):
  def top(self):
    return self \
    .annotate(heart_count=models.Count('hearts')) \
    .order_by('-heart_count', '-creation_timestamp')
  
  def viewable_by(self, user):
    fil = models.Q()
    if not user.is_superuser:
      fil = models.Q(is_private = False)
      if user.is_authenticated:
        fil = fil | models.Q(owner = user)

    return self.filter(fil)
  
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
  creation_timestamp = models.DateTimeField(auto_now_add=True)

  def is_hearted_by(self, user: User):
    return self.hearts.contains(user)
  
  def __str__(self) -> str:
    return f"{self.name} by {self.owner.username}"
    

class Comment(models.Model):
  deck = models.ForeignKey(Deck, on_delete=models.CASCADE, null=False)
  owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  text = models.TextField(blank=False, null=False)
  creation_timestamp = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    get_latest_by = 'creation_timestamp'

  def __str__(self) -> str:
    return f"{self.owner.username} commented on {self.deck.name} at {self.creation_timestamp}"