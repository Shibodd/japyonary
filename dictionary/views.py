from typing import Any, Dict
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms.search_bar import SearchBarForm
# Create your views here.

class IndexView(TemplateView):
  template_name = 'dictionary/index.html'

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    return {
      'search_bar_form': SearchBarForm()
    }