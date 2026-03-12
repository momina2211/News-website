"""API Views for recommendations and search"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from apps.articles.models import Article
from apps.analytics.recommendation_service import RecommendationService
from apps.search.services import SearchService
from apps.notifications.models import Notification


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RecommendationViewSet(viewsets.ViewSet):
    """
    API endpoints for personalized recommendations
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['get'])
    def recommended_for_me(self, request):
        """Get personalized article recommendations"""
        limit = request.query_params.get('limit', 10)
        recommendations = RecommendationService.get_recommendations(request.user, limit=int(limit))
        
        data = [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'summary': a.summary,
            'category': a.category.name if a.category else None,
            'author': a.author.get_full_name(),
            'trending_score': a.trending_score,
            'url': a.get_absolute_url()
        } for a in recommendations]
        
        return Response(data)

    @action(detail=False, methods=['get'])
    def similar(self, request):
        """Get articles similar to a given article"""
        article_slug = request.query_params.get('article', '')
        limit = request.query_params.get('limit', 5)
        
        try:
            article = Article.objects.get(slug=article_slug, status='published')
            similar = RecommendationService.get_similar_articles(article, limit=int(limit))
            
            data = [{
                'id': a.id,
                'title': a.title,
                'slug': a.slug,
                'summary': a.summary,
                'url': a.get_absolute_url()
            } for a in similar]
            
            return Response(data)
        except Article.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)


class SearchViewSet(viewsets.ViewSet):
    """
    API endpoints for advanced search
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search articles"""
        query = request.query_params.get('q', '')
        limit = request.query_params.get('limit', 20)
        
        if not query:
            return Response({'error': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = SearchService.search_articles(query, limit=int(limit))
        
        data = [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'summary': a.summary,
            'category': a.category.name if a.category else None,
            'tags': [t.name for t in a.tags.all()],
            'author': a.author.get_full_name(),
            'published_at': a.published_at,
            'url': a.get_absolute_url()
        } for a in results]
        
        return Response(data)

    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """Get search autocomplete suggestions"""
        query = request.query_params.get('q', '')
        limit = request.query_params.get('limit', 10)
        
        if len(query) < 2:
            return Response([])
        
        suggestions = SearchService.get_autocomplete_suggestions(query, limit=int(limit))
        return Response(suggestions)


class NotificationViewSet(viewsets.ViewSet):
    """
    API endpoints for notifications
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def list_notifications(self, request):
        """Get user's notifications"""
        limit = request.query_params.get('limit', 10)
        
        notifications = Notification.objects.filter(user=request.user)[:int(limit)]
        
        data = [{
            'id': n.id,
            'type': n.notification_type,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at,
            'url': n.url
        } for n in notifications]
        
        return Response(data)

    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Mark all notifications as read"""
        from apps.notifications.services import NotificationService
        
        count = NotificationService.mark_all_as_read(request.user)
        return Response({'marked_as_read': count})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})

