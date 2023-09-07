from typing import Any, Dict
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.generic import ListView
from django.http.request import HttpRequest
from japyonary.forms.search_bar import SearchBarForm
from decks import models

from japyonary import utils

# Create your views here.
class DeckSearchView(ListView):
  template_name = 'decks/search.html'
  model = models.Deck
  context_object_name = 'decks'
  paginate_by = 9

  def parse_parameters(self):
    self.query = utils.normalize_query(self.request.GET.get('query'))
    self.mode = utils.normalize_query(self.request.GET.get('mode'))
    self.is_searching = self.query is not None and self.mode is not None

  def get(self, request: HttpRequest, *args, **kwargs):
    self.parse_parameters()
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)
    ctx["is_searching"] = self.is_searching
    ctx["search_bar_form"] = SearchBarForm(
      placeholder='Enter a search query...',
      mode_choices=[
        ('author', 'By author'),
        ('title', 'By title'),
        ('description', 'By description'),
      ],
      data = utils.make_optional_dict(query=self.query, mode=self.mode)
    )
    return ctx
  
  def get_queryset(self) -> QuerySet[Any]:
    fil = Q()
    if not self.request.user.is_superuser:
      fil = Q(is_private = False)
      if self.request.user.is_authenticated:
        fil = fil | Q(owner = self.request.user)
    
    if self.is_searching:
      MODE_FILTER_LOOKUP = {
        'author': 'owner__username__icontains',
        'title': 'name__icontains',
        'description': 'description__icontains'
      }
      fil = fil & Q(**{ MODE_FILTER_LOOKUP[self.mode]: self.query })
    
    return models.Deck.objects.filter(fil).top()