from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views.generic import View, ListView
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from japyonary.forms.search_bar import SearchBarForm
from . import models, query_utils

class IndexView(ListView):
  template_name = 'dictionary/index.html'
  model = models.Entry
  context_object_name = 'entries'
  paginate_by = 10

  def __rewrite_bad_searchbar_url(self, request: HttpRequest):
    # TODO: just request it correctly client-side in the first place
    if 'query' in request.GET and 'lang' in request.GET:
      return redirect(reverse('dictionary:index', kwargs = {
        'query': request.GET['query'],
        'lang': request.GET['lang']
      }))
    
    return None
  
  def parse_parameters(self):
    def normalize(s: str):
      if s is None:
        return None
      s = s.strip()
      if len(s) == 0:
        return None
      return s

    self.query = normalize(self.request.resolver_match.kwargs.get('query'))
    self.lang = normalize(self.request.resolver_match.kwargs.get('lang'))
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

    if self.query:
      search_bar_data = {
        'query': self.query,
        'lang': self.lang
      }
    else:
      search_bar_data = {}

    ctx['search_bar_form'] = SearchBarForm(
      placeholder='Enter kanji, kana, romaji or english',
      mode_choices=[('en', 'English'), ('ja', 'Japanese')],
      mode_field_name='lang',
      data=search_bar_data
    )

    return ctx
  
  def get_queryset(self) -> QuerySet[Any]:
    if self.is_searching:
      return query_utils.get_entry_queryset(self.lang, self.query)
    else:
      return tuple()