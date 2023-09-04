from django.contrib import admin

# Register your models here.
class EntryAdmin(admin.ModelAdmin):
  search_fields = ('ent_seq', )
  pass