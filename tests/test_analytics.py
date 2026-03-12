"""Tests for trending algorithm and recommendations"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.articles.models import Article
from apps.categories.models import Category
from apps.analytics.trending_service import TrendingService
from apps.analytics.recommendation_service import RecommendationService
from apps.analytics.models import UserInteraction


class TrendingServiceTest(TestCase):
    """Test trending algorithm"""

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.category = Category.objects.create(name="Tech")
        self.article = Article.objects.create(
            title="Popular Article",
            summary="Summary",
            content="Content",
            author=self.author,
            category=self.category,
            status="published",
            view_count=100,
            like_count=50
        )

    def test_calculate_trending_score(self):
        """Test trending score calculation"""
        score = TrendingService.calculate_trending_score(self.article)
        # Score = (100 * 0.5) + (50 * 2) = 50 + 100 = 150
        self.assertEqual(score, 150)

    def test_get_trending_articles(self):
        """Test retrieving trending articles"""
        trending = TrendingService.get_trending_articles(limit=10)
        self.assertIsInstance(trending, list)

    def test_update_article_trending(self):
        """Test updating trending for single article"""
        TrendingService.update_article_trending(self.article)
        self.article.refresh_from_db()
        self.assertGreater(self.article.trending_score, 0)
        self.assertIsNotNone(self.article.last_trending_update)


class RecommendationServiceTest(TestCase):
    """Test personalized recommendations"""

    def setUp(self):
        self.user = User.objects.create_user("reader", password="pass")
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.tech_cat = Category.objects.create(name="Technology")
        self.python_tag = None  # Will create if needed

        # Create test article
        self.article = Article.objects.create(
            title="Python Tutorial",
            summary="Learn Python",
            content="Content " * 50,
            author=self.author,
            category=self.tech_cat,
            status="published"
        )

    def test_track_interaction(self):
        """Test tracking user interactions"""
        RecommendationService.track_interaction(self.user, self.article, "view")
        
        interaction = UserInteraction.objects.get(
            user=self.user,
            article=self.article,
            interaction_type="view"
        )
        self.assertEqual(interaction.user, self.user)

    def test_build_interests_from_history(self):
        """Test building user interests from history"""
        # Create some interactions
        for i in range(3):
            RecommendationService.track_interaction(self.user, self.article, "view")

        interests = RecommendationService.build_interests_from_history(self.user)
        self.assertIn(self.tech_cat.id, interests["categories"])

    def test_get_recommendations(self):
        """Test getting personalized recommendations"""
        # Create interaction history
        RecommendationService.track_interaction(self.user, self.article, "like")

        # Create another article to recommend
        article2 = Article.objects.create(
            title="Django Guide",
            summary="Learn Django",
            content="Content " * 50,
            author=self.author,
            category=self.tech_cat,
            status="published"
        )

        recommendations = RecommendationService.get_recommendations(self.user, limit=10)
        self.assertIsInstance(recommendations, list)

    def test_get_similar_articles(self):
        """Test finding similar articles"""
        similar = RecommendationService.get_similar_articles(self.article)
        self.assertIsInstance(similar, list)

