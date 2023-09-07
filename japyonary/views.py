from typing import Any, Dict
from django.views.generic import TemplateView
from japyonary.forms.search_bar import SearchBarForm
from decks.models import Deck
from django.urls import reverse

class HomepageView(TemplateView):
  template_name = "japyonary/homepage.html"

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)
    sbf = SearchBarForm(
      placeholder='Query the dictionary with kanji, kana, romaji or english',
      mode_choices=[('en', 'English'), ('ja', 'Japanese')],
      mode_field_name='lang'
    )
    sbf.helper.form_action = reverse('dictionary:index')

    ctx['dictionary_search_bar_form'] = sbf
    if self.request.user.is_authenticated:
      pass
    else:
      ctx['decks'] = Deck.objects.top()[:3]
    return ctx
