"""Trending Algorithm Service"""
from django.db.models import F, Q
from django.utils import timezone
from datetime import timedelta
from apps.articles.models import Article
import logging

logger = logging.getLogger(__name__)


class TrendingService:
    """Calculate and update trending scores for articles"""

    # Weight multipliers for engagement metrics
    VIEW_WEIGHT = 0.5
    LIKE_WEIGHT = 2.0
    COMMENT_WEIGHT = 1.5
    
    # Recency decay factor (articles lose relevance over time)
    RECENCY_DECAY = 0.02  # 2% per day

    @staticmethod
    def calculate_trending_score(article) -> float:
        """
        Calculate trending score using engagement metrics
        
        Formula: (views * 0.5) + (likes * 2) + (comments * 1.5) - recency_decay
        """
        # Get comment count
        comment_count = article.comments.filter(is_approved=True).count()
        
        # Calculate base score
        score = (
            (article.view_count * TrendingService.VIEW_WEIGHT) +
            (article.like_count * TrendingService.LIKE_WEIGHT) +
            (comment_count * TrendingService.COMMENT_WEIGHT)
        )
        
        # Apply recency decay (older articles score lower)
        if article.published_at:
            days_old = (timezone.now() - article.published_at).days
            decay = TrendingService.RECENCY_DECAY * days_old
            score = max(0, score - decay)
        
        return round(score, 2)

    @staticmethod
    def recalculate_all_trending() -> dict:
        """
        Recalculate trending scores for all published articles
        
        Returns:
            Dict with stats about update
        """
        stats = {
            "updated": 0,
            "errors": 0,
        }
        
        # Get all published articles from last 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        articles = Article.objects.filter(
            status="published",
            published_at__gte=cutoff_date
        )
        
        for article in articles:
            try:
                score = TrendingService.calculate_trending_score(article)
                article.trending_score = score
                article.last_trending_update = timezone.now()
                article.save(update_fields=["trending_score", "last_trending_update"])
                stats["updated"] += 1
            except Exception as e:
                logger.error(f"Error updating trending for article {article.id}: {str(e)}")
                stats["errors"] += 1
        
        return stats

    @staticmethod
    def get_trending_articles(limit: int = 10, days: int = 7):
        """Get top trending articles from recent period"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return Article.objects.filter(
            status="published",
            published_at__gte=cutoff_date
        ).order_by("-trending_score")[:limit]

    @staticmethod
    def update_article_trending(article) -> None:
        """Update trending score for a single article"""
        if article.status == "published":
            score = TrendingService.calculate_trending_score(article)
            article.trending_score = score
            article.last_trending_update = timezone.now()
            article.save(update_fields=["trending_score", "last_trending_update"])

