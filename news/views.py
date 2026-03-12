from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponse

from .models import Article, Category
from .forms import ArticleForm, ArticleDeleteForm, SearchForm


# ---------------------------------------------------------------------------
# Existing views
# ---------------------------------------------------------------------------

class HomeView(ListView):
    model = Article
    template_name = 'news/index.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        return Article.objects.filter(status='published').select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured_articles'] = Article.objects.filter(
            status='published', is_featured=True
        ).select_related('author', 'category')[:3]
        ctx['categories'] = Category.objects.all()
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx['related_articles'] = Article.objects.filter(
            status='published', category=article.category
        ).exclude(pk=article.pk).select_related('author', 'category')[:3]
        return ctx


class CategoryView(ListView):
    model = Article
    template_name = 'news/category.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Article.objects.filter(
            status='published', category=self.category
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = self.category
        return ctx


class SearchView(View):
    def get(self, request):
        form = SearchForm(request.GET)
        articles = []
        query = ''
        if form.is_valid():
            query = form.cleaned_data.get('q', '')
            if query:
                articles = Article.objects.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(excerpt__icontains=query),
                    status='published',
                ).select_related('author', 'category')

        if request.htmx:
            return render(request, 'partials/search_results.html', {
                'articles': articles,
                'query': query,
            })
        return render(request, 'news/search.html', {
            'form': form,
            'articles': articles,
            'query': query,
        })


class LoadMoreView(View):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        per_page = 6
        offset = (page - 1) * per_page
        articles = Article.objects.filter(status='published').select_related(
            'author', 'category'
        )[offset:offset + per_page]
        return render(request, 'partials/article_card.html', {'articles': articles})


# ---------------------------------------------------------------------------
# CRUD views
# ---------------------------------------------------------------------------

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff:
            return Article.objects.all().select_related('author', 'category')
        return Article.objects.filter(
            author=self.request.user
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['status_choices'] = Article.STATUS_CHOICES
        ctx['total_count'] = qs.count()
        ctx['published_count'] = qs.filter(status='published').count()
        ctx['draft_count'] = qs.filter(status='draft').count()
        return ctx


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Article '{form.instance.title}' created successfully!")
        return response

    def get_success_url(self):
        return reverse('article_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Create'
        ctx['page_title'] = 'Create New Article'
        return ctx


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.author or self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Article '{form.instance.title}' updated successfully!")
        return response

    def get_success_url(self):
        return reverse('article_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Update'
        ctx['page_title'] = f'Edit: {self.object.title}'
        return ctx


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.author or self.request.user.is_staff

    def get_form(self, form_class=None):
        if self.request.method == 'POST':
            return ArticleDeleteForm(self.request.POST)
        return ArticleDeleteForm()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            title = self.object.title
            self.object.delete()
            messages.success(request, f"Article '{title}' has been deleted.")
            return redirect(self.success_url)
        return render(request, self.template_name, {
            'article': self.object,
            'object': self.object,
            'form': form,
        })

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.get_form()
        return ctx
