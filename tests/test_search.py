"""Tests for search service"""
from django.test import TestCase
from apps.accounts.models import User
from apps.articles.models import Article
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.search.services import SearchService


class SearchServiceTest(TestCase):
    """Test advanced search functionality"""

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.category = Category.objects.create(name="Technology")
        self.python_tag = Tag.objects.create(name="Python")
        self.django_tag = Tag.objects.create(name="Django")

        # Create test articles
        self.article1 = Article.objects.create(
            title="Python Tutorial for Beginners",
            summary="Learn Python basics",
            content="Python is a great programming language. " * 20,
            author=self.author,
            category=self.category,
            status="published"
        )
        self.article1.tags.add(self.python_tag)

        self.article2 = Article.objects.create(
            title="Django Web Framework Guide",
            summary="Build web apps with Django",
            content="Django is built on Python. " * 20,
            author=self.author,
            category=self.category,
            status="published"
        )
        self.article2.tags.add(self.django_tag)

    def test_search_articles_by_title(self):
        """Test searching articles by title"""
        results = SearchService.search_articles("Python", limit=10)
        self.assertIn(self.article1, results)

    def test_search_articles_by_tag(self):
        """Test searching by tag"""
        results = SearchService.search_by_tag("Python")
        self.assertIn(self.article1, results)

    def test_search_by_category(self):
        """Test searching by category"""
        results = SearchService.search_by_category("technology")
        self.assertIn(self.article1, results)

    def test_search_by_author(self):
        """Test searching by author"""
        results = SearchService.search_by_author("author")
        self.assertIn(self.article1, results)

    def test_get_autocomplete_suggestions(self):
        """Test autocomplete suggestions"""
        suggestions = SearchService.get_autocomplete_suggestions("Py")
        self.assertGreater(len(suggestions), 0)

    def test_empty_search_returns_none(self):
        """Test that empty search returns no results"""
        results = SearchService.search_articles("")
        self.assertEqual(len(list(results)), 0)

