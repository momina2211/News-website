"""Tags views"""
from django.views.generic import DetailView
from django.conf import settings
from django.core.paginator import Paginator
from .models import Tag


class TagDetailView(DetailView):
    model = Tag
    template_name = "tags/tag_page.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        articles = self.object.articles.filter(status="published").order_by("-published_at")
        paginator = Paginator(articles, getattr(settings, "ARTICLES_PER_PAGE", 12))
        page = self.request.GET.get("page", 1)
        ctx["articles"] = paginator.get_page(page)
        ctx["popular_tags"] = Tag.objects.all()[:20]
        return ctx

