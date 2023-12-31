from typing import Any, Optional
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import CreateView, UpdateView
from decks.models import Deck

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Div
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from decks.views.mixins import DeckEditPermissionTestMixin
from japyonary import utils

class CreateUpdateDeckFormMixin():
  fields = [ 'name', 'description', 'is_private', 'cover_image' ]
  slug_field = 'id'
  submit_text = 'Submit'

  def get_success_url(self) -> str:
    return reverse('decks:deck_detail', kwargs={ 'slug': self.object.pk })

  def get_form(self, form_class=None):
    form = super().get_form(form_class)
    form.helper = FormHelper()
    form.helper.layout = Layout(
      *self.fields,
      Div(
        Submit('submit', self.submit_text, css_class='btn-primary px-5'),
        HTML('<span class="flex-grow-1"></span>'),
        HTML(f"""<a class="btn btn-danger px-5" href="{ self.get_cancel_url() }"> Cancel </a>"""),
        css_class = 'd-flex'
      )
    )
    return form

class DeckCreateView(utils.StatusBarFormValidationMixin, LoginRequiredMixin, CreateUpdateDeckFormMixin, CreateView):
  model = Deck
  template_name = "decks/deck_create.html"
  submit_text = 'Create'
  status_bar_message_on_success = "Deck created successfully!"

  def form_valid(self, form: BaseModelForm) -> HttpResponse:
    form.instance.owner = self.request.user
    return super().form_valid(form)
  
  def get_cancel_url(self):
    return reverse('decks:deck_search')

class DeckUpdateView(LoginRequiredMixin, DeckEditPermissionTestMixin, utils.StatusBarFormValidationMixin, CreateUpdateDeckFormMixin, UpdateView):
  model = Deck
  template_name = "decks/deck_update.html"
  submit_text = 'Update'
  status_bar_message_on_success = "Deck updated successfully."

  def get_cancel_url(self):
    return self.get_success_url()