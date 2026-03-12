"""Accounts app URLs"""
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/me/", views.ProfileUpdateView.as_view(), name="profile_update"),
]

