from django.urls import path
from django.contrib.auth import views as auth_views
import users.views

app_name = 'users'

urlpatterns = [
  path("login", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
  path("signup", users.views.SignUpView.as_view(), name="signup"),
  path("logout", auth_views.LogoutView.as_view(), name="logout")
]