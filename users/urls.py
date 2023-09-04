from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
  path("<str:username>", views.UserView.as_view(), name="user_profile")
]