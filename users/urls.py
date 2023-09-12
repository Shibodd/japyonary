from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
  path("login", views.LoginView.as_view(template_name="users/login.html"), name="login"),
  path("signup", views.SignUpView.as_view(), name="signup"),
  path("logout", views.LogoutView.as_view(), name="logout")
]