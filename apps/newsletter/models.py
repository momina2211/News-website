"""Newsletter app models"""
from django.db import models


class Subscriber(models.Model):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True, db_index=True)
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletter_subscription"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    last_newsletter_sent = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-subscribed_at"]
        indexes = [
            models.Index(fields=["is_active", "email"]),
        ]

    def __str__(self):
        return self.email

    def unsubscribe(self):
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["is_active", "unsubscribed_at"])

    def subscribe(self):
        self.is_active = True
        self.unsubscribed_at = None
        self.save(update_fields=["is_active", "unsubscribed_at"])


class NewsletterEmail(models.Model):
    """Newsletter emails sent"""
    subject = models.CharField(max_length=200)
    content = models.TextField()
    articles = models.ManyToManyField("articles.Article", related_name="newsletters")
    sent_at = models.DateTimeField(auto_now_add=True)
    total_recipients = models.PositiveIntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.subject} - {self.sent_at.date()}"

