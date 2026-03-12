"""Categories views"""
from django.views.generic import DetailView
from django.conf import settings
from .models import Category
from apps.articles.models import Article


class CategoryDetailView(DetailView):
    model = Category
    template_name = "categories/category_page.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        articles = self.object.articles.filter(status="published").order_by("-published_at")
        from django.core.paginator import Paginator
        paginator = Paginator(articles, getattr(settings, "ARTICLES_PER_PAGE", 12))
        page = self.request.GET.get("page", 1)
        ctx["articles"] = paginator.get_page(page)
        ctx["all_categories"] = Category.objects.all()
        return ctx

