"""Comments app models"""
from django.db import models


class Comment(models.Model):
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["article", "is_approved"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on '{self.article.title}'"

