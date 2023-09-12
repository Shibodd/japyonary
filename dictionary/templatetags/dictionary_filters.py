from django import template
from dictionary import models
from django.db.models import Count
import itertools

register = template.Library()

@register.filter
def entry_get_main_reb(entry: models.Entry):
  if entry.rele_set.count() > 1:
    return entry.rele_set.annotate(count=Count('re_pri')).order_by('-count').values('reb').first()['reb']
  else:
    return entry.rele_set.first().reb

@register.filter
def entry_get_main_keb(entry: models.Entry):
  kele_count = entry.kele_set.count()
  if kele_count > 0:
    if kele_count > 1:
      return entry.kele_set.annotate(count=Count('ke_pri')).order_by('-count').values('keb').first()['keb']
    else:
      return entry.kele_set.first().keb
  else:
    return None
  
@register.filter
def sense_get_glosses_str(sense: models.Sense):
  return ', '.join((g['content'] for g in sense.gloss_set.values('content')))

@register.filter
def sense_get_only_applies_to(sense: models.Sense):
  stag = itertools.chain(
    (x['keb'] for x in sense.stagk.values('keb')),
    (x['reb'] for x in sense.stagr.values('reb'))
  )
  return ', '.join(stag)