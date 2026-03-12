from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.HomeView.as_view(), name='home'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('load-more/', views.LoadMoreView.as_view(), name='load_more'),

    # CRUD views (auth required)
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
]
