"""Search app models"""
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class SearchIndex(models.Model):
    """Full-text search index for articles"""
    article = models.OneToOneField(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="search_index"
    )
    title_vector = SearchVectorField(null=True, blank=True)
    content_vector = SearchVectorField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GinIndex(fields=["title_vector"]),
            GinIndex(fields=["content_vector"]),
        ]

    def __str__(self):
        return f"Index - {self.article.title}"


class SearchAutocomplete(models.Model):
    """Cache for search autocomplete suggestions"""
    query = models.CharField(max_length=100, unique=True, db_index=True)
    suggestion_count = models.PositiveIntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_searched"]

    def __str__(self):
        return self.query

