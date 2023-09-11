from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views.generic import ListView
from django.http.request import HttpRequest

from japyonary.forms.search_bar import SearchBarForm
from . import models

import romkan
import re
from . import models
from django.db.models import Count

class DictionarySearchView(ListView):
  template_name = 'dictionary/index.html'
  model = models.Entry
  context_object_name = 'entries'
  paginate_by = 10

  def __init__(self, **kwargs: Any) -> None:
    super().__init__(**kwargs)
    self.show_all_with_no_query = False
  
  def get(self, request: HttpRequest, *args, **kwargs):
    self.search_bar_form = SearchBarForm(
      placeholder='Enter kanji, kana, romaji or english',
      mode_choices=[('en', 'English'), ('ja', 'Japanese')],
      mode_field_name='lang',
      data = request.GET
    )
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)

    ctx['is_searching'] = self.search_bar_form.is_valid()
    ctx['search_bar_form'] = self.search_bar_form
    return ctx
  
  def get_base_queryset(self) -> QuerySet[models.Entry]:
    return models.Entry.objects

  def get_queryset(self) -> QuerySet[Any]:
    if self.search_bar_form.is_valid():
      query = self.search_bar_form.cleaned_data['query']
      lang = self.search_bar_form.cleaned_data['lang']

      if query and lang:
        return self.__get_queryset(self.__build_filter(lang, query))
    
    if self.show_all_with_no_query:
      return self.__get_queryset()
    else:
      return tuple()
  
  __is_valid_romaji = re.compile(f'^({romkan.HEPPAT.pattern})*$')
  def __build_filter(self, lang: str, user_query: str):
    user_query = user_query.strip().lower()

    if lang == 'en':
      fil = { 'sense__gloss__content__icontains': user_query }
    else:
      hep = romkan.to_hepburn(user_query)
      # If it is all romaji it doesn't make any sense to look in KEle (REle is guaranteed to contain it too).
      # If it is not all romaji, it doesn't make any sense to look in REle (REle will never contain it).

      if DictionarySearchView.__is_valid_romaji.match(hep):
        fil = { 'rele__hepburn__contains': hep }
      else:
        fil = { 'kele__hepburn__contains': hep }

    return fil

  def __get_queryset(self, fil = None):
    qs = self.get_base_queryset()
    if fil:
      qs = qs.filter(**fil)
    
    return qs.annotate(pri_count=Count('kele__ke_pri') + Count('rele__re_pri')) \
             .order_by('-pri_count', 'ent_seq') \
             .prefetch_everything()