from typing import Any, Dict
from django.db.models.query import QuerySet
from django.views.generic import View, ListView
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms.search_bar import SearchBarForm
from . import models, query_utils

class IndexView(ListView):
  template_name = 'dictionary/index.html'
  model = models.Entry
  context_object_name = 'entries'
  paginate_by = 10

  def __rewrite_bad_searchbar_url(self, request: HttpRequest):
    # TODO: just request it correctly client-side in the first place
    if 'query' in request.GET:
      return redirect(reverse('dictionary:index', kwargs = {
        'query': request.GET['query']
      }))
    return None

  def get(self, request: HttpRequest, *args, **kwargs):
    rewrite_resp = self.__rewrite_bad_searchbar_url(request)
    return rewrite_resp or super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    context = super().get_context_data(**kwargs)
    query = self.request.resolver_match.kwargs.get('query', None)

    sbf =  SearchBarForm() if query is None else SearchBarForm({ 'query': query })
    context['search_bar_form'] = sbf
    return context
  
  def get_queryset(self) -> QuerySet[Any]:
    query = query_utils.build_query(self.request.resolver_match.kwargs.get('query'))
    return models.Entry.objects.filter(query)