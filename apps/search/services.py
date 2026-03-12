"""Advanced Search Service with PostgreSQL Full-Text Search"""
from django.db.models import Q, F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from apps.articles.models import Article
from apps.tags.models import Tag
from apps.categories.models import Category
from apps.search.models import SearchAutocomplete
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Advanced search with ranking"""

    @staticmethod
    def search_articles(query: str, limit: int = 20):
        """
        Full-text search across articles with ranking
        
        Searches:
        - Article title
        - Article content  
        - Tags
        - Category
        """
        if not query or len(query.strip()) < 2:
            return Article.objects.none()
        
        # Try to use full-text search if PostgreSQL
        try:
            search_query = SearchQuery(query, search_type='websearch')
            
            # Search vectors for title and content
            search_vector = SearchVector('title', weight='A') + \
                            SearchVector('summary', weight='B') + \
                            SearchVector('content', weight='C')
            
            results = Article.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(search=search_query) | Q(status="published"),
                status="published"
            ).order_by('-rank')[:limit]
            
            return results
            
        except Exception as e:
            # Fallback to standard search
            logger.warning(f"Full-text search failed, using fallback: {str(e)}")
            return SearchService._fallback_search(query, limit)

    @staticmethod
    def _fallback_search(query: str, limit: int = 20):
        """Fallback search without PostgreSQL FTS"""
        q = Q(status="published")
        q &= (
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query)
        )
        
        return Article.objects.filter(q).distinct().order_by(
            "-published_at"
        )[:limit]

    @staticmethod
    def search_by_tag(tag_name: str, limit: int = 20):
        """Search articles by tag"""
        try:
            tag = Tag.objects.get(name__iexact=tag_name)
            return Article.objects.filter(
                tags=tag,
                status="published"
            ).order_by("-published_at")[:limit]
        except Tag.DoesNotExist:
            return Article.objects.none()

    @staticmethod
    def search_by_category(category_slug: str, limit: int = 20):
        """Search articles by category"""
        try:
            category = Category.objects.get(slug=category_slug)
            return Article.objects.filter(
                category=category,
                status="published"
            ).order_by("-published_at")[:limit]
        except Category.DoesNotExist:
            return Article.objects.none()

    @staticmethod
    def search_by_author(author_username: str, limit: int = 20):
        """Search articles by author"""
        return Article.objects.filter(
            author__username__iexact=author_username,
            status="published"
        ).order_by("-published_at")[:limit]

    @staticmethod
    def get_autocomplete_suggestions(query: str, limit: int = 10) -> list:
        """Get search autocomplete suggestions"""
        if not query or len(query.strip()) < 2:
            return []
        
        suggestions = set()
        
        # Article titles
        titles = Article.objects.filter(
            title__istartswith=query,
            status="published"
        ).values_list("title", flat=True)[:limit]
        suggestions.update(titles)
        
        # Tags
        tags = Tag.objects.filter(
            name__istartswith=query
        ).values_list("name", flat=True)[:limit]
        suggestions.update([f"#{tag}" for tag in tags])
        
        # Categories
        categories = Category.objects.filter(
            name__istartswith=query
        ).values_list("name", flat=True)[:limit]
        suggestions.update([f"in:{cat}" for cat in categories])
        
        # Track search
        SearchAutocomplete.objects.update_or_create(
            query=query,
            defaults={"suggestion_count": len(suggestions)}
        )
        
        return list(suggestions)[:limit]

    @staticmethod
    def update_search_index(article) -> None:
        """Update search index for article"""
        try:
            from apps.search.models import SearchIndex
            from django.contrib.postgres.search import SearchVector
            
            search_index, created = SearchIndex.objects.get_or_create(article=article)
            
            # Update vectors
            search_index.title_vector = SearchVector('title')
            search_index.content_vector = SearchVector('content')
            search_index.save()
            
        except Exception as e:
            logger.error(f"Error updating search index: {str(e)}")

