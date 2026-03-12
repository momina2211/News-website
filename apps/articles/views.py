"""Articles views"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView
)
from django.conf import settings
from django.urls import reverse_lazy

from .models import Article, ArticleLike
from .forms import ArticleForm, ArticleSearchForm
from apps.categories.models import Category
from apps.tags.models import Tag


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        published = Article.objects.filter(status="published").select_related("author", "category")
        ctx["featured_article"] = published.filter(is_featured=True).order_by("-published_at").first()
        ctx["hero_articles"] = published.order_by("-published_at")[:4]
        ctx["latest_articles"] = published.order_by("-published_at")[4:16]
        ctx["trending_articles"] = published.order_by("-view_count")[:5]
        ctx["categories"] = Category.objects.all()[:8]
        ctx["popular_tags"] = Tag.objects.all()[:20]
        return ctx


class ArticleListView(ListView):
    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        return Article.objects.filter(status="published").select_related(
            "author", "category"
        ).prefetch_related("tags").order_by("-published_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["title"] = "All Articles"
        return ctx

    def get(self, request, *args, **kwargs):
        # Support HTMX infinite scroll - return partial
        if request.headers.get("HX-Request") and request.GET.get("page"):
            self.template_name = "partials/article_cards.html"
        return super().get(request, *args, **kwargs)


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        queryset = Article.objects.select_related(
            "author", "category"
        ).prefetch_related("tags")
        user = self.request.user
        if user.is_authenticated:
            if getattr(user, "is_editor", False) or getattr(user, "is_admin_user", False):
                return queryset
            return queryset.filter(Q(status="published") | Q(author=user))
        return queryset.filter(status="published")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count atomically for public views only
        if obj.status == Article.Status.PUBLISHED:
            Article.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx["related_articles"] = article.get_related_articles(4)
        ctx["approved_comments"] = article.comments.filter(
            is_approved=True
        ).select_related("user").order_by("created_at")
        ctx["comment_count"] = ctx["approved_comments"].count()

        # Permission flags for template
        ctx["user_can_edit"] = (
            self.request.user.is_authenticated and article.can_be_edited_by(self.request.user)
        )

        # Check if current user has liked
        if self.request.user.is_authenticated:
            ctx["user_liked"] = ArticleLike.objects.filter(
                article=article, user=self.request.user
            ).exists()
        else:
            ctx["user_liked"] = False

        return ctx


class AuthorArticleListView(ListView):
    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        from apps.accounts.models import User
        self.author = get_object_or_404(User, username=self.kwargs["username"])
        return Article.objects.filter(
            author=self.author, status="published"
        ).select_related("author", "category").order_by("-published_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Articles by {self.author.get_full_name() or self.author.username}"
        ctx["profile_user"] = self.author
        return ctx


class SearchView(ListView):
    model = Article
    template_name = "search/search_results.html"
    context_object_name = "articles"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        if not self.query:
            return Article.objects.none()
        return Article.objects.filter(
            Q(title__icontains=self.query)
            | Q(summary__icontains=self.query)
            | Q(content__icontains=self.query)
            | Q(tags__name__icontains=self.query)
            | Q(author__username__icontains=self.query),
            status="published",
        ).distinct().select_related("author", "category").order_by("-published_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.query
        ctx["result_count"] = self.get_queryset().count()
        return ctx


# ─── Author/Editor article management ────────────────────────────────────────

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_author:
            messages.error(request, "You need author permissions to create articles.")
            return redirect("articles:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Article created as draft.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("articles:article_detail", kwargs={"slug": self.object.slug})


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_form.html"

    def dispatch(self, request, *args, **kwargs):
        article = self.get_object()
        if not article.can_be_edited_by(request.user):
            messages.error(request, "You do not have permission to edit this article.")
            return redirect("articles:article_detail", slug=article.slug)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Article updated successfully.")
        return super().form_valid(form)


class ArticleSubmitReviewView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        try:
            article.submit_for_review(request.user)
            messages.success(request, "Article submitted for review.")
        except (PermissionError, ValueError) as e:
            messages.error(request, str(e))
        return redirect("articles:article_detail", slug=slug)


class ArticlePublishView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        try:
            article.publish(request.user)
            messages.success(request, "Article published successfully!")
        except PermissionError as e:
            messages.error(request, str(e))
        return redirect("articles:article_detail", slug=slug)


class ArticleRejectView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        reason = request.POST.get("reason", "")
        try:
            article.reject(request.user, reason)
            messages.success(request, "Article rejected.")
        except PermissionError as e:
            messages.error(request, str(e))
        return redirect("articles:article_detail", slug=slug)


# ─── HTMX Views ──────────────────────────────────────────────────────────────

class ArticleLikeView(LoginRequiredMixin, View):
    """HTMX endpoint: toggle article like."""

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, status="published")
        like, created = ArticleLike.objects.get_or_create(
            article=article, user=request.user
        )
        if not created:
            like.delete()
            Article.objects.filter(pk=article.pk).update(like_count=F("like_count") - 1)
            liked = False
        else:
            Article.objects.filter(pk=article.pk).update(like_count=F("like_count") + 1)
            liked = True

        article.refresh_from_db(fields=["like_count"])

        if request.headers.get("HX-Request"):
            from django.template.loader import render_to_string
            html = render_to_string(
                "partials/like_button.html",
                {"article": article, "user_liked": liked},
                request=request,
            )
            return HttpResponse(html)
        return JsonResponse({"liked": liked, "like_count": article.like_count})


class LoadMoreArticlesView(ListView):
    """HTMX: load more articles (infinite scroll)."""
    model = Article
    template_name = "partials/article_cards.html"
    context_object_name = "articles"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        return Article.objects.filter(status="published").select_related(
            "author", "category"
        ).order_by("-published_at")

