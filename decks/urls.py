from django.urls import path

from . import views

app_name = 'decks'

urlpatterns = [
  path("", views.SearchView.as_view(), name="index"),
  path("view/<int:deck_id>", views.SearchView.as_view(), name="deck_detail")
]