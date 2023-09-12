from django.urls import path

from . import views

app_name = 'decks'

urlpatterns = [
  path("", views.DeckSearchView.as_view(), name="deck_search"),
  path("view/<slug:slug>", views.DeckDetailView.as_view(), name="deck_detail"),
  path("deck_to_srs", views.DeckToSrsView.as_view(), name="deck_to_srs"),
  path("create", views.DeckCreateView.as_view(), name="deck_create"),
  path("delete/<slug:slug>", views.DeckDeleteView.as_view(), name="deck_delete"),
  path("update/<slug:slug>", views.DeckUpdateView.as_view(), name="deck_update"),
  path("clone", views.DeckCloneView.as_view(), name="deck_clone"),
  path("vocabulary/<slug:slug>", views.DeckVocabularyView.as_view(), name="deck_vocabulary"),
  path("vocabulary/edit/<slug:slug>", views.DeckVocabularyView.as_view(), name="deck_vocabulary_edit"),
  path("ajax/heart_deck", views.ajax.heart_deck, name="heart_deck"),
  path("ajax/toggle_entry_from_deck", views.ajax.toggle_entry_from_deck, name="toggle_entry_from_deck"),
]