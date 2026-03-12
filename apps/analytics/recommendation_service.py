"""Personalized Article Recommendation Engine"""
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
from apps.articles.models import Article
from apps.analytics.models import UserInteraction, UserInterest
from apps.categories.models import Category
from apps.tags.models import Tag
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Generate personalized article recommendations"""

    @staticmethod
    def get_user_interests(user) -> dict:
        """Get user's category and tag interests with weights"""
        interests = UserInterest.objects.filter(user=user)
        
        categories = {}
        tags = {}
        
        for interest in interests:
            if interest.category:
                categories[interest.category.id] = interest.weight
            if interest.tag:
                tags[interest.tag.id] = interest.weight
        
        return {"categories": categories, "tags": tags}

    @staticmethod
    def build_interests_from_history(user) -> dict:
        """Build user interests from viewing/engagement history"""
        interactions = UserInteraction.objects.filter(user=user)
        
        # Get categories and tags from viewed articles
        category_weights = {}
        tag_weights = {}
        
        for interaction in interactions:
            # Category weight
            if interaction.article.category:
                cat_id = interaction.article.category.id
                weight = category_weights.get(cat_id, 1.0)
                if interaction.interaction_type == "like":
                    weight += 2.0
                elif interaction.interaction_type == "comment":
                    weight += 1.5
                category_weights[cat_id] = weight
            
            # Tag weights
            for tag in interaction.article.tags.all():
                tag_id = tag.id
                weight = tag_weights.get(tag_id, 1.0)
                if interaction.interaction_type == "like":
                    weight += 2.0
                elif interaction.interaction_type == "comment":
                    weight += 1.5
                tag_weights[tag_id] = weight
        
        # Store in UserInterest model
        for cat_id, weight in category_weights.items():
            category = Category.objects.get(id=cat_id)
            UserInterest.objects.update_or_create(
                user=user,
                category=category,
                tag=None,
                defaults={"weight": min(weight, 5.0)}
            )
        
        for tag_id, weight in tag_weights.items():
            tag = Tag.objects.get(id=tag_id)
            UserInterest.objects.update_or_create(
                user=user,
                category=None,
                tag=tag,
                defaults={"weight": min(weight, 5.0)}
            )
        
        return {"categories": category_weights, "tags": tag_weights}

    @staticmethod
    def get_recommendations(user, limit: int = 10) -> list:
        """
        Get personalized article recommendations for user
        
        Algorithm:
        1. Get user interests from history
        2. Find articles in similar categories
        3. Find articles with similar tags
        4. Sort by engagement (trending_score)
        5. Exclude already viewed articles
        """
        # Build interests from history
        interests = RecommendationService.build_interests_from_history(user)
        
        # Get recently viewed articles (last 30 days)
        recent_interactions = UserInteraction.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values_list("article_id", flat=True)
        
        # Query similar articles
        q = Q()
        
        # By categories
        if interests["categories"]:
            q |= Q(category_id__in=interests["categories"].keys())
        
        # By tags
        if interests["tags"]:
            q |= Q(tags__id__in=interests["tags"].keys())
        
        # Get published articles, excluding already viewed
        recommendations = Article.objects.filter(
            q,
            status="published",
            published_at__lte=timezone.now()
        ).exclude(
            id__in=recent_interactions
        ).exclude(
            author=user  # Exclude own articles
        ).distinct().order_by(
            "-trending_score",
            "-published_at"
        )[:limit]
        
        return list(recommendations)

    @staticmethod
    def track_interaction(user, article, interaction_type: str) -> None:
        """Track user interaction with article"""
        if not user.is_authenticated:
            return
        
        UserInteraction.objects.update_or_create(
            user=user,
            article=article,
            interaction_type=interaction_type,
            defaults={}
        )
        
        # Update user interests
        RecommendationService.build_interests_from_history(user)

    @staticmethod
    def get_similar_articles(article, limit: int = 5) -> list:
        """Get similar articles based on tags and category"""
        similar = Article.objects.filter(
            Q(category=article.category) |
            Q(tags__in=article.tags.all()),
            status="published",
            published_at__lte=timezone.now()
        ).exclude(
            id=article.id
        ).distinct().order_by(
            "-published_at"
        )[:limit]
        
        return list(similar)

