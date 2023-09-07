import json
from typing import Any, Dict
from django.views.generic import DetailView
from decks import models
from decks.forms import AddCommentForm
from japyonary import utils
from django import http
from django.core.exceptions import BadRequest, PermissionDenied

from django.shortcuts import redirect
from django.urls import reverse
from decks.views.mixins import DeckViewPermissionTestMixin

class DeckDetailView(DeckViewPermissionTestMixin, DetailView):
  template_name = 'decks/detail.html'
  model = models.Deck
  context_object_name = 'deck'
  slug_field = 'id'

  def post(self, request: http.HttpRequest, slug, *args, **kwargs):
    login_required_resp = utils.login_required_test(request)
    if login_required_resp is not None:
      return login_required_resp
    
    form = AddCommentForm(request.POST)
    if not form.is_valid():
      raise BadRequest("Invalid request")
    
    deck = self.get_object()
    if deck.is_private:
      raise PermissionDenied("Cannot add comments to a private deck.")

    models.Comment.objects.create(
      deck = deck,
      owner = request.user,
      text = form.cleaned_data['text']
    )

    return redirect(reverse('decks:deck_detail', kwargs = {
      'slug': slug
    }))

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)
    ctx["add_comment_form"] = AddCommentForm()
    return ctx