"""Articles URLs"""
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("articles/", views.ArticleListView.as_view(), name="article_list"),
    path("articles/new/", views.ArticleCreateView.as_view(), name="article_create"),
    path("articles/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("articles/<slug:slug>/edit/", views.ArticleUpdateView.as_view(), name="article_update"),
    path("articles/<slug:slug>/submit/", views.ArticleSubmitReviewView.as_view(), name="article_submit"),
    path("articles/<slug:slug>/publish/", views.ArticlePublishView.as_view(), name="article_publish"),
    path("articles/<slug:slug>/reject/", views.ArticleRejectView.as_view(), name="article_reject"),
    path("articles/<slug:slug>/like/", views.ArticleLikeView.as_view(), name="article_like"),
    path("articles/more/", views.LoadMoreArticlesView.as_view(), name="load_more"),
    path("author/<str:username>/", views.AuthorArticleListView.as_view(), name="author_articles"),
    path("search/", views.SearchView.as_view(), name="search"),
]

