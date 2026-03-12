"""NewsHub URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from apps.articles.sitemaps import ArticleSitemap, StaticViewSitemap

sitemaps = {
    "articles": ArticleSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.articles.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("categories/", include("apps.categories.urls")),
    path("tags/", include("apps.tags.urls")),
    path("comments/", include("apps.comments.urls")),
    path("api/", include("apps.ai.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

