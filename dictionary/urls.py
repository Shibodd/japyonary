from django.urls import path

from . import views

app_name = 'dictionary'

urlpatterns = [
  path("", views.DictionarySearchView.as_view(), name="index"),
  path("<str:lang>/<str:query>", views.DictionarySearchView.as_view(), name="index")
]