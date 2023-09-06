from typing import Optional, Type
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import CreateView
from decks.models import Deck

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Div
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class DeckCreateView(LoginRequiredMixin, CreateView):
  model = Deck
  template_name = "decks/deck_create.html"
  fields = [ 'name', 'description', 'is_private', 'cover_image' ]

  def get_form(self, form_class=None):
    form = super().get_form(form_class)

    form.helper = FormHelper()
    form.helper.layout = Layout(
      *DeckCreateView.fields,
      Div(
        Submit('submit', 'Create', css_class='btn-primary px-5'),
        HTML('<span class="flex-grow-1"></span>'),
        HTML(f"""<a class="btn btn-danger px-5" href="{ reverse('decks:deck_search') }"> Cancel </a>"""),
        css_class = 'd-flex'
      )
    )
    return form
  
  def form_valid(self, form: BaseModelForm) -> HttpResponse:
    form.instance.owner = self.request.user
    return super().form_valid(form)
  
  def get_success_url(self) -> str:
    return reverse('decks:deck_detail', kwargs={ 'slug': self.object.pk })