"""Tests for AI services"""
from django.test import TestCase
from apps.accounts.models import User
from apps.articles.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.ai.services import AISummaryService
from apps.ai.tag_service import AITagRecommendationService
from apps.ai.headline_service import AIHeadlineService


class AISummaryServiceTest(TestCase):
    """Test AI summary generation"""

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.category = Category.objects.create(name="Tech")
        self.article = Article.objects.create(
            title="Test Article",
            summary="Test summary",
            content="Test content " * 100,
            author=self.author,
            category=self.category,
            status="published"
        )

    def test_summary_service_initialization(self):
        """Test summary service can be initialized"""
        service = AISummaryService()
        self.assertIsNotNone(service)

    def test_generate_summary_requires_api_key(self):
        """Test that summary generation returns None without API key"""
        service = AISummaryService()
        service.api_key = ""
        result = service.generate_summary(self.article)
        self.assertIsNone(result)


class AITagRecommendationTest(TestCase):
    """Test AI tag recommendations"""

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.category = Category.objects.create(name="Tech")
        self.article = Article.objects.create(
            title="Test Article",
            summary="Test summary",
            content="Test content " * 100,
            author=self.author,
            category=self.category,
            status="draft"
        )

    def test_tag_service_initialization(self):
        """Test tag recommendation service can be initialized"""
        service = AITagRecommendationService()
        self.assertIsNotNone(service)

    def test_get_tag_recommendations_without_api(self):
        """Test tag recommendations return empty list without API key"""
        service = AITagRecommendationService()
        service.api_key = ""
        result = service.get_tag_recommendations(self.article)
        self.assertEqual(result, [])


class AIHeadlineServiceTest(TestCase):
    """Test AI headline generation"""

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.category = Category.objects.create(name="Tech")
        self.article = Article.objects.create(
            title="Test Article",
            summary="Test summary",
            content="Test content " * 100,
            author=self.author,
            category=self.category,
            status="draft"
        )

    def test_headline_service_initialization(self):
        """Test headline service can be initialized"""
        service = AIHeadlineService()
        self.assertIsNotNone(service)

    def test_generate_headlines_without_api(self):
        """Test headline generation returns empty list without API key"""
        service = AIHeadlineService()
        service.api_key = ""
        result = service.generate_headlines(self.article)
        self.assertEqual(result, [])

