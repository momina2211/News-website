"""Notifications app models"""
from django.db import models


class Notification(models.Model):
    """User notifications for comments, approvals, etc."""
    NOTIFICATION_TYPES = [
        ("comment_reply", "Comment Reply"),
        ("article_approved", "Article Approved"),
        ("article_rejected", "Article Rejected"),
        ("new_follower_article", "New Article from Followed Author"),
        ("mention", "Mentioned in Comment"),
        ("like", "Article Liked"),
    ]

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=500)
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    related_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_created"
    )
    url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.message}"

    def mark_as_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class FollowAuthor(models.Model):
    """Users following authors"""
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="following"
    )
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "author")

    def __str__(self):
        return f"{self.user} follows {self.author}"

