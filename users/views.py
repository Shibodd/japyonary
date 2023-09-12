from typing import Any
from django import http
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import CreateView
from django.urls import reverse_lazy
from users.forms import SignupForm
from japyonary import utils
from django.contrib.auth import views as auth_views

class SignUpView(utils.StatusBarFormValidationMixin, utils.StatusBarContextMixin, CreateView):
  form_class = SignupForm
  template_name = "users/signup.html"
  success_url = reverse_lazy('users:login')
  status_bar_message_on_success = "You're now signed up - welcome aboard! Now please login."

class LoginView(utils.StatusBarFormValidationMixin, utils.StatusBarContextMixin, auth_views.LoginView):
  status_bar_message_on_success = "Logged in successfully - Welcome back!"

class LogoutView(utils.StatusBarContextMixin, auth_views.LogoutView):
  def dispatch(self, request, *args: Any, **kwargs: Any):
    ans = super().dispatch(request, *args, **kwargs)
    utils.add_statusbar_message(request, "Logged out successfully - See you again!")
    return ans