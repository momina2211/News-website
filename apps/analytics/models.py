"""Analytics app models"""
from django.db import models
from django.contrib.gis.geoip2 import GeoIP2


class ArticleView(models.Model):
    """Track article views for analytics"""
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="view_records"
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_views"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    session_id = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["article", "viewed_at"]),
            models.Index(fields=["user", "viewed_at"]),
            models.Index(fields=["viewed_at"]),
        ]

    def __str__(self):
        return f"{self.article.title} - {self.viewed_at}"


class UserInteraction(models.Model):
    """Track user interactions for recommendations"""
    INTERACTION_TYPES = [
        ("view", "Viewed"),
        ("like", "Liked"),
        ("comment", "Commented"),
        ("bookmark", "Bookmarked"),
        ("share", "Shared"),
    ]

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="interactions"
    )
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="user_interactions"
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("user", "article", "interaction_type")
        indexes = [
            models.Index(fields=["user", "interaction_type"]),
            models.Index(fields=["article", "interaction_type"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_interaction_type_display()} - {self.article}"


class UserInterest(models.Model):
    """Track user interests by category and tags"""
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="interests"
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_interests"
    )
    tag = models.ForeignKey(
        "tags.Tag",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_interests"
    )
    weight = models.FloatField(default=1.0, help_text="Interest strength (1.0-5.0)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["user", "category", "tag"]]

    def __str__(self):
        category_name = self.category.name if self.category else self.tag.name
        return f"{self.user} - {category_name} ({self.weight})"

