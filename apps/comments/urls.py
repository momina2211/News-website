"""Comments URLs"""
from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("<slug:article_slug>/", views.CommentListView.as_view(), name="comment_list"),
    path("<slug:article_slug>/post/", views.CommentCreateView.as_view(), name="comment_create"),
]

