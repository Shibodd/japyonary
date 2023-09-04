from django.contrib import admin
from . import  models


class DeckAdmin(admin.ModelAdmin):
  raw_id_fields = ("dictionary_entries", )

# Register your models here.
admin.site.register(models.Deck, DeckAdmin)