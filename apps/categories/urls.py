"""Categories URLs"""
from django.urls import path
from . import views

app_name = "categories"

urlpatterns = [
    path("<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
]

