import romkan
import re
from . import models
from django.db.models import Count, Sum, F, Expression

is_valid_romaji = re.compile(f'^({romkan.HEPPAT.pattern})*$')

def get_entry_queryset(lang: str, user_query: str):
  user_query = user_query.strip().lower()

  if lang == 'en':
    fil = { 'sense__gloss__content__icontains': user_query }
  else:
    hep = romkan.to_hepburn(user_query)
    # If it is all romaji it doesn't make any sense to look in KEle (REle is guaranteed to contain it too).
    # If it is not all romaji, it doesn't make any sense to look in REle (REle will never contain it).

    if is_valid_romaji.match(hep):
      fil = { 'rele__hepburn__contains': hep }
    else:
      fil = { 'kele__hepburn__contains': hep }

  return models.Entry.objects \
    .filter(**fil) \
    .annotate(pri_count=Count('kele__ke_pri') + Count('rele__re_pri')) \
    .order_by('-pri_count')