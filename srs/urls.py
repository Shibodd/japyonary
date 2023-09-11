from django.urls import path

from . import views

app_name = 'srs'

urlpatterns = [
  path("", views.SrsReviewView.as_view(), name="srs_review"),
  path("ajax/add_flashcard", views.add_remove_entry_in_srs, name="srs_review"),
]