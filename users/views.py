from django.views.generic import CreateView
from django.urls import reverse_lazy
from users.forms import SignupForm

class SignUpView(CreateView):
  form_class = SignupForm
  template_name = "users/signup.html"
  success_url = reverse_lazy('users:login')