from django.contrib import admin
from srs import models

# Register your models here.
class SrsAdmin(admin.ModelAdmin):
  readonly_fields = ['entry']

# Register your models here.
admin.site.register(models.Flashcard, SrsAdmin)