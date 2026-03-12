from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError

from .models import Category, Article
from .forms import ArticleForm, ArticleDeleteForm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_article_data(category, slug='test-article-form', status='draft'):
    return {
        'title': 'Test Article Form',
        'slug': slug,
        'content': 'This is test content for the article.',
        'excerpt': 'Test excerpt',
        'category': category.pk,
        'status': status,
        'is_featured': False,
        'published_date': '',
    }


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Technology', slug='technology')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Technology')
        self.assertEqual(self.category.slug, 'technology')

    def test_category_str_representation(self):
        self.assertEqual(str(self.category), 'Technology')

    def test_category_slug_unique(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Technology Duplicate', slug='technology')

    def test_category_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertIn('technology', url)

    def test_category_ordering(self):
        Category.objects.create(name='Sports', slug='sports')
        Category.objects.create(name='Arts', slug='arts')
        categories = list(Category.objects.all())
        names = [c.name for c in categories]
        self.assertEqual(names, sorted(names))


class ArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='This is test content for the article.',
            excerpt='Test excerpt',
            author=self.user,
            category=self.category,
            status='published',
            published_date=timezone.now(),
        )

    def test_article_creation(self):
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.slug, 'test-article')
        self.assertEqual(self.article.author, self.user)
        self.assertEqual(self.article.category, self.category)
        self.assertEqual(self.article.status, 'published')

    def test_article_str_representation(self):
        self.assertEqual(str(self.article), self.article.title)

    def test_article_default_status_is_draft(self):
        article = Article.objects.create(
            title='Draft Article',
            slug='draft-article',
            content='Content.',
            author=self.user,
        )
        self.assertEqual(article.status, 'draft')

    def test_article_get_absolute_url(self):
        url = self.article.get_absolute_url()
        self.assertIn('test-article', url)

    def test_article_views_count_default_zero(self):
        article = Article.objects.create(
            title='Zero Views',
            slug='zero-views',
            content='Content.',
            author=self.user,
        )
        self.assertEqual(article.views_count, 0)

    def test_article_ordering(self):
        now = timezone.now()
        older = Article.objects.create(
            title='Older Article',
            slug='older-article',
            content='Content.',
            author=self.user,
            status='published',
            published_date=now - timezone.timedelta(days=2),
        )
        newer = Article.objects.create(
            title='Newer Article',
            slug='newer-article',
            content='Content.',
            author=self.user,
            status='published',
            published_date=now - timezone.timedelta(days=1),
        )
        articles = list(Article.objects.filter(status='published'))
        # Ordering is newest first (-published_date)
        pub_dates = [a.published_date for a in articles if a.published_date]
        for i in range(len(pub_dates) - 1):
            self.assertGreaterEqual(pub_dates[i], pub_dates[i + 1])


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class ArticleFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='This is test content for the article.',
            excerpt='Test excerpt',
            author=self.user,
            category=self.category,
            status='published',
            published_date=timezone.now(),
        )

    # --- Positive ---

    def test_valid_article_form(self):
        data = make_article_data(self.category)
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_saves_article_with_author(self):
        data = make_article_data(self.category, slug='saved-article')
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        article = form.save(commit=False)
        article.author = self.user
        article.save()
        self.assertTrue(Article.objects.filter(slug='saved-article').exists())

    def test_create_published_article_auto_sets_published_date(self):
        data = make_article_data(self.category, slug='auto-published', status='published')
        data['published_date'] = ''
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNotNone(form.cleaned_data.get('published_date'))

    def test_update_article_form(self):
        data = make_article_data(self.category, slug='test-article', status='published')
        data['title'] = 'Updated Title'
        form = ArticleForm(instance=self.article, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.title, 'Updated Title')

    # --- Negative ---

    def test_form_missing_title(self):
        data = make_article_data(self.category)
        data.pop('title')
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_missing_content(self):
        data = make_article_data(self.category)
        data.pop('content')
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_form_invalid_slug_with_spaces(self):
        data = make_article_data(self.category, slug='invalid slug')
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)

    def test_form_invalid_slug_special_characters(self):
        data = make_article_data(self.category, slug='invalid@slug!')
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)

    def test_form_duplicate_slug(self):
        Article.objects.create(
            title='Existing',
            slug='existing-slug',
            content='Content.',
            author=self.user,
        )
        data = make_article_data(self.category, slug='existing-slug')
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_title_too_long(self):
        data = make_article_data(self.category)
        data['title'] = 'a' * 301
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())


# ---------------------------------------------------------------------------
# View tests — shared setup
# ---------------------------------------------------------------------------

class BaseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.staff_user = User.objects.create_user(
            username='staffuser', password='testpass123', is_staff=True
        )
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='This is test content for the article.',
            excerpt='Test excerpt',
            author=self.user,
            category=self.category,
            status='published',
            published_date=timezone.now(),
        )

    def login(self, username='testuser', password='testpass123'):
        self.client.login(username=username, password=password)

    def _create_data(self, slug='new-article'):
        return {
            'title': 'New Article Title',
            'slug': slug,
            'content': 'Content for the new article.',
            'excerpt': 'Excerpt.',
            'category': self.category.pk,
            'status': 'draft',
            'is_featured': False,
            'published_date': '',
        }


# ---------------------------------------------------------------------------
# ArticleCreateView tests
# ---------------------------------------------------------------------------

class ArticleCreateViewTest(BaseViewTest):

    def test_create_view_accessible_when_logged_in(self):
        self.login()
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_article_success(self):
        self.login()
        response = self.client.post(reverse('article_create'), data=self._create_data())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(slug='new-article').exists())

    def test_create_article_sets_author_to_current_user(self):
        self.login()
        self.client.post(reverse('article_create'), data=self._create_data())
        article = Article.objects.filter(slug='new-article').first()
        self.assertIsNotNone(article)
        self.assertEqual(article.author, self.user)

    def test_create_article_success_message(self):
        self.login()
        response = self.client.post(
            reverse('article_create'), data=self._create_data(), follow=True
        )
        messages_list = list(response.context['messages'])
        self.assertTrue(any('created successfully' in str(m) for m in messages_list))

    # --- Negative ---

    def test_create_view_redirects_anonymous_user(self):
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_article_invalid_data(self):
        self.login()
        data = self._create_data()
        data['title'] = ''
        response = self.client.post(reverse('article_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_create_article_invalid_slug(self):
        self.login()
        data = self._create_data(slug='bad slug!')
        response = self.client.post(reverse('article_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('slug', response.context['form'].errors)

    def test_create_article_empty_post(self):
        self.login()
        response = self.client.post(reverse('article_create'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


# ---------------------------------------------------------------------------
# ArticleUpdateView tests
# ---------------------------------------------------------------------------

class ArticleUpdateViewTest(BaseViewTest):

    def test_update_view_accessible_by_author(self):
        self.login()
        response = self.client.get(reverse('article_edit', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)

    def test_update_view_accessible_by_staff(self):
        self.login(username='staffuser')
        response = self.client.get(reverse('article_edit', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)

    def test_update_article_success(self):
        self.login()
        data = self._create_data(slug=self.article.slug)
        data['title'] = 'Updated Title'
        response = self.client.post(
            reverse('article_edit', kwargs={'slug': self.article.slug}), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated Title')

    def test_update_article_success_message(self):
        self.login()
        data = self._create_data(slug=self.article.slug)
        data['title'] = 'Updated Title Again'
        response = self.client.post(
            reverse('article_edit', kwargs={'slug': self.article.slug}),
            data=data,
            follow=True,
        )
        messages_list = list(response.context['messages'])
        self.assertTrue(any('updated successfully' in str(m) for m in messages_list))

    # --- Negative ---

    def test_update_view_forbidden_for_non_author(self):
        self.login(username='otheruser')
        response = self.client.get(reverse('article_edit', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 403)

    def test_update_view_redirects_anonymous_user(self):
        response = self.client.get(reverse('article_edit', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 302)

    def test_update_article_invalid_data(self):
        self.login()
        data = self._create_data(slug=self.article.slug)
        data['title'] = ''
        response = self.client.post(
            reverse('article_edit', kwargs={'slug': self.article.slug}), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_update_nonexistent_article(self):
        self.login()
        response = self.client.get(reverse('article_edit', kwargs={'slug': 'nonexistent-slug'}))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# ArticleDeleteView tests
# ---------------------------------------------------------------------------

class ArticleDeleteViewTest(BaseViewTest):

    def _make_article(self, slug='article-to-delete'):
        return Article.objects.create(
            title='Article To Delete',
            slug=slug,
            content='Content.',
            author=self.user,
            category=self.category,
            status='published',
            published_date=timezone.now(),
        )

    def test_delete_view_accessible_by_author(self):
        self.login()
        response = self.client.get(reverse('article_delete', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)

    def test_delete_article_success(self):
        self.login()
        article = self._make_article()
        response = self.client.post(
            reverse('article_delete', kwargs={'slug': article.slug}),
            data={'confirm': True},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Article.objects.filter(slug=article.slug).exists())

    def test_delete_article_success_message(self):
        self.login()
        article = self._make_article(slug='msg-delete-article')
        response = self.client.post(
            reverse('article_delete', kwargs={'slug': article.slug}),
            data={'confirm': True},
            follow=True,
        )
        messages_list = list(response.context['messages'])
        self.assertTrue(any('has been deleted' in str(m) for m in messages_list))

    def test_delete_view_accessible_by_staff(self):
        self.login(username='staffuser')
        response = self.client.get(reverse('article_delete', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)

    # --- Negative ---

    def test_delete_view_forbidden_for_non_author(self):
        self.login(username='otheruser')
        response = self.client.get(reverse('article_delete', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 403)

    def test_delete_view_redirects_anonymous_user(self):
        response = self.client.get(reverse('article_delete', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 302)

    def test_delete_without_confirm(self):
        self.login()
        article = self._make_article(slug='no-confirm-article')
        self.client.post(
            reverse('article_delete', kwargs={'slug': article.slug}),
            data={'confirm': False},
        )
        self.assertTrue(Article.objects.filter(slug=article.slug).exists())

    def test_delete_nonexistent_article(self):
        self.login()
        response = self.client.get(reverse('article_delete', kwargs={'slug': 'nonexistent-slug'}))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# ArticleListView tests
# ---------------------------------------------------------------------------

class ArticleListViewTest(BaseViewTest):

    def test_list_view_shows_only_own_articles(self):
        Article.objects.create(
            title='Other User Article',
            slug='other-user-article',
            content='Content.',
            author=self.other_user,
        )
        self.login()
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        for article in articles:
            self.assertEqual(article.author, self.user)

    def test_staff_list_view_shows_all_articles(self):
        Article.objects.create(
            title='Other Article',
            slug='other-article',
            content='Content.',
            author=self.other_user,
        )
        self.login(username='staffuser')
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.context['total_count'], 2)

    def test_list_view_redirects_anonymous(self):
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 302)

    def test_list_view_pagination(self):
        # Create 15 articles total (1 already exists from setUp)
        for i in range(14):
            Article.objects.create(
                title=f'Paginated Article {i}',
                slug=f'paginated-article-{i}',
                content='Content.',
                author=self.user,
            )
        self.login()
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['articles']), 10)

        response_p2 = self.client.get(reverse('article_list') + '?page=2')
        self.assertEqual(response_p2.status_code, 200)
        self.assertEqual(len(response_p2.context['articles']), 5)


# ---------------------------------------------------------------------------
# SearchView tests
# ---------------------------------------------------------------------------

class SearchViewTest(BaseViewTest):

    def test_search_returns_matching_articles(self):
        response = self.client.get(reverse('search') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        titles = [a.title for a in articles]
        self.assertIn('Test Article', titles)

    def test_search_no_results(self):
        response = self.client.get(reverse('search') + '?q=xyznonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['articles']), 0)

    def test_search_htmx_returns_partial(self):
        response = self.client.get(
            reverse('search') + '?q=Test',
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'<html', response.content)

    def test_search_case_insensitive(self):
        response = self.client.get(reverse('search') + '?q=test')
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        titles = [a.title for a in articles]
        self.assertIn('Test Article', titles)
