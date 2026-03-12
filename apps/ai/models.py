"""AI app models"""
from django.db import models


class AITagSuggestion(models.Model):
    """AI-suggested tags for articles"""
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="ai_tag_suggestions"
    )
    tag = models.ForeignKey(
        "tags.Tag",
        on_delete=models.CASCADE,
        related_name="ai_suggestions"
    )
    confidence_score = models.FloatField(default=0.0, help_text="0.0 to 1.0")
    was_approved = models.BooleanField(null=True, blank=True, help_text="True if approved, False if rejected")
    suggested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "tag")
        ordering = ["-confidence_score"]

    def __str__(self):
        return f"{self.article.title} - {self.tag.name} ({self.confidence_score:.2f})"


class AIHeadlineSuggestion(models.Model):
    """AI-generated headline suggestions"""
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="ai_headline_suggestions"
    )
    full_headline = models.CharField(max_length=300)
    short_headline = models.CharField(max_length=100)
    social_headline = models.CharField(max_length=150)
    relevance_score = models.FloatField(default=0.0)
    was_used = models.BooleanField(default=False)
    suggested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-relevance_score"]

    def __str__(self):
        return f"{self.article.title} - {self.full_headline[:50]}"


class AIModel(models.Model):
    """Track AI models and versions"""
    name = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, choices=[
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("local", "Local Model"),
    ])
    model_id = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.provider})"

