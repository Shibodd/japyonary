import json
from typing import Any, Dict
from django.views.generic import DetailView
from decks import models
from decks.forms import AddCommentForm
from japyonary import utils
from django import http

from django.shortcuts import redirect
from django.urls import reverse

class DeckDetailView(DetailView):
  template_name = 'decks/detail.html'
  model = models.Deck
  context_object_name = 'deck'
  slug_field = 'id'

  def handle_add_comment_form(self, request, slug, form):
    if not form.is_valid():
      return False
    
    models.Comment.objects.create(
      deck = models.Deck.objects.get(pk = slug),
      owner = request.user,
      text = form.cleaned_data['text']
    )
    return True
  
  def post(self, request: http.HttpRequest, *args, **kwargs):
    login_required_resp = utils.login_required_test(request)
    if login_required_resp is not None:
      return login_required_resp

    slug = request.resolver_match.kwargs.get('slug')
    if slug is None:
      return http.HttpResponseBadRequest("Invalid request")
    
    ok = self.handle_add_comment_form(request, slug, AddCommentForm(request.POST))
    if not ok:
      return http.HttpResponseBadRequest("Invalid request")

    return redirect(reverse('decks:deck_detail', kwargs = {
      'slug': slug
    }))
    

  def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
    ctx = super().get_context_data(**kwargs)
    ctx["add_comment_form"] = AddCommentForm()
    return ctx