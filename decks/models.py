from django.db import models
from users.models import User
from dictionary.models import Entry

# Create your models here.
class Deck(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='owned_decks')
  dictionary_entries = models.ManyToManyField(Entry)
  hearts = models.ManyToManyField(User, related_name='hearted_decks')

  name = models.CharField(max_length=64, null=False, blank=False)
  description = models.TextField(blank=True, null=True)
  is_private = models.BooleanField(null=False, default=True)
  cover_image = models.ImageField(upload_to='deck_cover_images', blank=True)

class Comment(models.Model):
  deck = models.ForeignKey(Deck, on_delete=models.CASCADE, null=False)
  owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  text = models.TextField(blank=False, null=False)
  creation_timestamp = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    get_latest_by = 'creation_timestamp'