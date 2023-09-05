from django.urls import path

from . import views

app_name = 'decks'

urlpatterns = [
  path("", views.DeckSearchView.as_view(), name="deck_search"),
  path("view/<slug:slug>", views.DeckDetailView.as_view(), name="deck_detail"),
  path("ajax/heart_deck", views.ajax.heart_deck, name="heart_deck")
]