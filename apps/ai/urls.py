"""URLs for AI app"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .api_views import RecommendationViewSet, SearchViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'notifications', NotificationViewSet, basename='notifications')

app_name = 'ai'

urlpatterns = router.urls

