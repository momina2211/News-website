"""Tests for views: Home, ArticleList, ArticleDetail, Search, Auth."""
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.categories.models import Category
from apps.tags.models import Tag
from apps.articles.models import Article
from apps.comments.models import Comment


def make_published_article(author, category, title="Test Article View Title Here"):
    return Article.objects.create(
        title=title,
        summary="Summary text for view test article is here.",
        content="Content body for view tests.",
        author=author,
        category=category,
        status="published",
    )


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user("auth", password="pass", role="author")
        self.cat = Category.objects.create(name="News")

    def test_home_page_returns_200(self):
        r = self.client.get(reverse("articles:home"))
        self.assertEqual(r.status_code, 200)

    def test_home_shows_published_article(self):
        a = make_published_article(self.author, self.cat, "Breaking News Today Story Big")
        r = self.client.get(reverse("articles:home"))
        self.assertContains(r, a.title)

    def test_home_hides_draft_articles(self):
        Article.objects.create(
            title="Draft Article Not Shown Here",
            summary="Summary of draft article for hiding.",
            content="Content",
            author=self.author,
            category=self.cat,
            status="draft",
        )
        r = self.client.get(reverse("articles:home"))
        self.assertNotContains(r, "Draft Article Not Shown")


class ArticleListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user("auth2", password="pass", role="author")
        self.cat = Category.objects.create(name="Tech")

    def test_article_list_returns_200(self):
        r = self.client.get(reverse("articles:article_list"))
        self.assertEqual(r.status_code, 200)

    def test_pagination_works(self):
        for i in range(15):
            make_published_article(self.author, self.cat, title=f"Article Number {i:02d} Long Title Here")
        r = self.client.get(reverse("articles:article_list"))
        self.assertEqual(r.status_code, 200)
        r2 = self.client.get(reverse("articles:article_list") + "?page=2")
        self.assertEqual(r2.status_code, 200)


class ArticleDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user("detailauth", password="pass", role="author")
        self.cat = Category.objects.create(name="Science")

    def test_detail_returns_200_for_published(self):
        a = make_published_article(self.author, self.cat, "Published Article Detail View Test")
        r = self.client.get(a.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_detail_returns_404_for_draft(self):
        a = Article.objects.create(
            title="Draft Only Article Not Public",
            summary="Summary for draft article that should return 404.",
            content="Content",
            author=self.author,
            category=self.cat,
            status="draft",
        )
        r = self.client.get(a.get_absolute_url())
        self.assertEqual(r.status_code, 404)

    def test_detail_increments_view_count(self):
        a = make_published_article(self.author, self.cat, "View Count Increment Test Article")
        initial = a.view_count
        self.client.get(a.get_absolute_url())
        a.refresh_from_db()
        self.assertEqual(a.view_count, initial + 1)


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user("srchauth", password="pass", role="author")
        self.cat = Category.objects.create(name="World")

    def test_search_returns_200(self):
        r = self.client.get(reverse("articles:search") + "?q=test")
        self.assertEqual(r.status_code, 200)

    def test_search_finds_matching_article(self):
        a = make_published_article(self.author, self.cat, "Quantum Computing Breakthrough Today News")
        r = self.client.get(reverse("articles:search") + "?q=quantum")
        self.assertContains(r, "Quantum")

    def test_search_empty_query(self):
        r = self.client.get(reverse("articles:search") + "?q=")
        self.assertEqual(r.status_code, 200)


class CommentSpamProtectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("spammer", password="pass")
        self.author = User.objects.create_user("spamauth", password="pass", role="author")
        self.cat = Category.objects.create(name="General")
        self.article = make_published_article(self.author, self.cat, "Article For Spam Test Here")
        self.client.login(username="spammer", password="pass")

    def test_spam_comment_content_rejected(self):
        r = self.client.post(
            reverse("comments:comment_create", args=[self.article.slug]),
            {"content": "aaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
            HTTP_HX_REQUEST="true",
        )
        # Should return 422 (form error)
        self.assertEqual(r.status_code, 422)

    def test_comment_too_short_rejected(self):
        r = self.client.post(
            reverse("comments:comment_create", args=[self.article.slug]),
            {"content": "Hi"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(r.status_code, 422)

