from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views.generic import View, ListView
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from japyonary.forms.search_bar import SearchBarForm
from . import models, query_utils
from japyonary import utils

class IndexView(ListView):
  template_name = 'dictionary/index.html'
  model = models.Entry
  context_object_name = 'entries'
  paginate_by = 10

  def __rewrite_bad_searchbar_url(self, request: HttpRequest):
    # TODO: just request it correctly client-side in the first place
    query = request.GET.get('query')
    lang = request.GET.get('lang')

    if not query and not lang:
      return None
    
    if query and lang:
      return redirect(reverse('dictionary:index', kwargs = {
        'query': query,
        'lang': lang
      }))

    return redirect(reverse('dictionary:index'))
  
  def parse_parameters(self):
    self.query = utils.normalize_query(self.request.resolver_match.kwargs.get('query'))
    self.lang = utils.normalize_query(self.request.resolver_match.kwargs.get('lang'))
    self.is_searching = self.query is not None and self.lang is not None

  def get(self, request: HttpRequest, *args, **kwargs):
    rewrite_resp = self.__rewrite_bad_searchbar_url(request)
    if rewrite_resp:
      return rewrite_resp
    
    self.parse_parameters()
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)

    ctx['is_searching'] = self.is_searching

    ctx['search_bar_form'] = SearchBarForm(
      placeholder='Enter kanji, kana, romaji or english',
      mode_choices=[('en', 'English'), ('ja', 'Japanese')],
      mode_field_name='lang',
      data = utils.make_optional_dict(query=self.query, lang=self.lang)
    )

    return ctx
  
  def get_queryset(self) -> QuerySet[Any]:
    if self.is_searching:
      return query_utils.get_entry_queryset(self.lang, self.query)
    else:
      return tuple()