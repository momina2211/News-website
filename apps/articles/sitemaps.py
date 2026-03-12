"""Articles sitemaps"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(status="published").order_by("-published_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["articles:home", "articles:article_list"]

    def location(self, item):
        return reverse(item)

