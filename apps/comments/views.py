"""Comments views — fully HTMX-compatible"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from apps.articles.models import Article
from .models import Comment
from .forms import CommentForm


class CommentListView(View):
    """HTMX: load approved comments for an article."""

    def get(self, request, article_slug):
        article = get_object_or_404(Article, slug=article_slug, status="published")
        comments = article.comments.filter(
            is_approved=True, parent=None
        ).select_related("user").prefetch_related("replies__user")
        form = CommentForm()
        html = render_to_string(
            "partials/comments.html",
            {"comments": comments, "article": article, "form": form, "user": request.user},
            request=request,
        )
        return HttpResponse(html)


class CommentCreateView(LoginRequiredMixin, View):
    """HTMX: submit a new comment without page reload."""

    def post(self, request, article_slug):
        article = get_object_or_404(Article, slug=article_slug, status="published")
        form = CommentForm(request.POST)

        # Spam protection: rate limit — max 5 comments per hour per user
        from django.utils import timezone
        from datetime import timedelta
        recent_count = Comment.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(hours=1),
        ).count()
        if recent_count >= 5:
            form.add_error(None, "You've posted too many comments recently. Please wait.")

        if form.is_valid():
            parent_id = request.POST.get("parent_id")
            parent = None
            if parent_id:
                parent = Comment.objects.filter(pk=parent_id, article=article).first()

            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.parent = parent
            # Auto-approve for editors/admins
            if request.user.is_editor or request.user.is_admin_user:
                comment.is_approved = True
            comment.save()

            comments = article.comments.filter(
                is_approved=True, parent=None
            ).select_related("user").prefetch_related("replies__user")
            html = render_to_string(
                "partials/comments.html",
                {
                    "comments": comments,
                    "article": article,
                    "form": CommentForm(),
                    "user": request.user,
                    "success_message": "Your comment has been submitted and is awaiting approval."
                    if not comment.is_approved else None,
                },
                request=request,
            )
            return HttpResponse(html)

        # Return form with errors
        html = render_to_string(
            "partials/comment_form.html",
            {"form": form, "article": article},
            request=request,
        )
        return HttpResponse(html, status=422)

