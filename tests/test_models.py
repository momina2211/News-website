"""Tests for models: User, Category, Tag, Article, Comment."""
from django.test import TestCase
from django.utils.text import slugify
from apps.accounts.models import User
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.articles.models import Article
from apps.comments.models import Comment


class UserModelTest(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user(username="reader1", password="pass", role="reader")
        self.author = User.objects.create_user(username="author1", password="pass", role="author")
        self.editor = User.objects.create_user(username="editor1", password="pass", role="editor")
        self.admin = User.objects.create_user(username="admin1", password="pass", role="admin", is_superuser=True)

    def test_is_author_role(self):
        self.assertTrue(self.author.is_author)
        self.assertFalse(self.reader.is_author)

    def test_is_editor_role(self):
        self.assertTrue(self.editor.is_editor)
        self.assertFalse(self.author.is_editor)

    def test_avatar_url_fallback(self):
        url = self.reader.get_avatar_url()
        self.assertIn("ui-avatars.com", url)

    def test_str(self):
        self.assertIn("reader1", str(self.reader))


class CategoryModelTest(TestCase):
    def test_slug_auto_generated(self):
        cat = Category.objects.create(name="World News")
        self.assertEqual(cat.slug, "world-news")

    def test_unique_slug(self):
        Category.objects.create(name="Tech")
        with self.assertRaises(Exception):
            Category.objects.create(name="Tech")

    def test_str(self):
        cat = Category.objects.create(name="Sports")
        self.assertEqual(str(cat), "Sports")


class TagModelTest(TestCase):
    def test_slug_auto_generated(self):
        tag = Tag.objects.create(name="Artificial Intelligence")
        self.assertEqual(tag.slug, "artificial-intelligence")

    def test_str(self):
        tag = Tag.objects.create(name="Python")
        self.assertEqual(str(tag), "Python")


class ArticleModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="writer", password="pass", role="author")
        self.editor = User.objects.create_user(username="editor", password="pass", role="editor")
        self.category = Category.objects.create(name="Technology")

    def _make_article(self, **kwargs):
        defaults = dict(
            title="Test Article Title Long Enough",
            summary="This is a good summary for testing purposes.",
            content="Article content goes here for testing.",
            author=self.author,
            category=self.category,
        )
        defaults.update(kwargs)
        return Article.objects.create(**defaults)

    def test_slug_auto_generated(self):
        article = self._make_article(title="My First Article Post Here")
        self.assertEqual(article.slug, "my-first-article-post-here")

    def test_duplicate_slug_gets_suffix(self):
        a1 = self._make_article(title="Duplicate Title Article Here")
        a2 = self._make_article(title="Duplicate Title Article Here")
        self.assertNotEqual(a1.slug, a2.slug)
        self.assertTrue(a2.slug.endswith("-1"))

    def test_default_status_is_draft(self):
        article = self._make_article()
        self.assertEqual(article.status, "draft")

    def test_reading_time(self):
        content = " ".join(["word"] * 400)
        article = self._make_article(content=content)
        self.assertEqual(article.reading_time, 2)

    def test_meta_description_auto_populated(self):
        summary = "This is an auto-populated meta description test summary."
        article = self._make_article(summary=summary)
        self.assertEqual(article.meta_description, summary[:160])

    def test_workflow_submit_for_review(self):
        article = self._make_article()
        article.submit_for_review(self.author)
        self.assertEqual(article.status, "pending_review")

    def test_workflow_publish(self):
        article = self._make_article()
        article.submit_for_review(self.author)
        article.publish(self.editor)
        self.assertEqual(article.status, "published")
        self.assertIsNotNone(article.published_at)

    def test_workflow_reject(self):
        article = self._make_article()
        article.submit_for_review(self.author)
        article.reject(self.editor, reason="Needs more research")
        self.assertEqual(article.status, "rejected")
        self.assertEqual(article.rejection_reason, "Needs more research")

    def test_can_be_edited_by_author_only_in_draft(self):
        article = self._make_article()
        self.assertTrue(article.can_be_edited_by(self.author))
        article.submit_for_review(self.author)
        self.assertFalse(article.can_be_edited_by(self.author))
        self.assertTrue(article.can_be_edited_by(self.editor))

    def test_absolute_url(self):
        article = self._make_article()
        self.assertIn(article.slug, article.get_absolute_url())


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="commenter", password="pass")
        self.author = User.objects.create_user(username="auth", password="pass", role="author")
        self.cat = Category.objects.create(name="General")
        self.article = Article.objects.create(
            title="Article For Comments Test",
            summary="Summary for comments test article here.",
            content="Content",
            author=self.author,
            category=self.cat,
            status="published",
        )

    def test_comment_created(self):
        comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            content="This is a great article!",
        )
        self.assertEqual(comment.article, self.article)
        self.assertFalse(comment.is_approved)

    def test_str(self):
        comment = Comment.objects.create(article=self.article, user=self.user, content="Nice!")
        self.assertIn("commenter", str(comment))

