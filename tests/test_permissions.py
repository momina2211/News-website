"""Tests for article workflow permissions."""
from django.test import TestCase
from apps.accounts.models import User
from apps.categories.models import Category
from apps.articles.models import Article


def make_article(author, category, **kwargs):
    defaults = dict(
        title="Permission Test Article Long Title",
        summary="Summary for the permission test article here.",
        content="Content body",
        author=author,
        category=category,
        status="draft",
    )
    defaults.update(kwargs)
    return Article.objects.create(**defaults)


class ArticleWorkflowTest(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user("reader", password="pass", role="reader")
        self.author = User.objects.create_user("author", password="pass", role="author")
        self.author2 = User.objects.create_user("author2", password="pass", role="author")
        self.editor = User.objects.create_user("editor", password="pass", role="editor")
        self.superuser = User.objects.create_superuser("super", password="pass", email="s@s.com")
        self.cat = Category.objects.create(name="Test Cat")

    # ── submit_for_review ──
    def test_author_can_submit_own_draft(self):
        a = make_article(self.author, self.cat)
        a.submit_for_review(self.author)
        self.assertEqual(a.status, "pending_review")

    def test_other_author_cannot_submit(self):
        a = make_article(self.author, self.cat)
        with self.assertRaises(PermissionError):
            a.submit_for_review(self.author2)

    def test_reader_cannot_submit(self):
        a = make_article(self.author, self.cat)
        with self.assertRaises(PermissionError):
            a.submit_for_review(self.reader)

    def test_cannot_submit_already_pending(self):
        a = make_article(self.author, self.cat, status="pending_review")
        with self.assertRaises(ValueError):
            a.submit_for_review(self.author)

    # ── publish ──
    def test_editor_can_publish(self):
        a = make_article(self.author, self.cat, status="pending_review")
        a.publish(self.editor)
        self.assertEqual(a.status, "published")
        self.assertIsNotNone(a.published_at)

    def test_author_cannot_publish(self):
        a = make_article(self.author, self.cat, status="pending_review")
        with self.assertRaises(PermissionError):
            a.publish(self.author)

    def test_publishing_without_review_by_author_raises(self):
        a = make_article(self.author, self.cat, status="draft")
        with self.assertRaises(PermissionError):
            a.publish(self.author)

    def test_superuser_can_publish_any(self):
        a = make_article(self.author, self.cat, status="draft")
        a.publish(self.superuser)
        self.assertEqual(a.status, "published")

    # ── reject ──
    def test_editor_can_reject(self):
        a = make_article(self.author, self.cat, status="pending_review")
        a.reject(self.editor, reason="Too short")
        self.assertEqual(a.status, "rejected")

    def test_author_cannot_reject(self):
        a = make_article(self.author, self.cat, status="pending_review")
        with self.assertRaises(PermissionError):
            a.reject(self.author)

    # ── can_be_edited_by ──
    def test_author_can_edit_draft(self):
        a = make_article(self.author, self.cat)
        self.assertTrue(a.can_be_edited_by(self.author))

    def test_author_cannot_edit_pending(self):
        a = make_article(self.author, self.cat, status="pending_review")
        self.assertFalse(a.can_be_edited_by(self.author))

    def test_editor_can_edit_any(self):
        a = make_article(self.author, self.cat, status="pending_review")
        self.assertTrue(a.can_be_edited_by(self.editor))

    def test_other_author_cannot_edit(self):
        a = make_article(self.author, self.cat)
        self.assertFalse(a.can_be_edited_by(self.author2))

