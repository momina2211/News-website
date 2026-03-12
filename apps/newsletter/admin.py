"""Admin configuration for newsletter app"""
from django.contrib import admin
from .models import Subscriber, NewsletterEmail


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "is_active", "subscribed_at", "last_newsletter_sent")
    list_filter = ("is_active", "subscribed_at", "last_newsletter_sent")
    search_fields = ("email", "user__username")
    readonly_fields = ("subscribed_at", "unsubscribed_at", "last_newsletter_sent")
    fieldsets = (
        ("Subscriber Info", {
            "fields": ("email", "user")
        }),
        ("Status", {
            "fields": ("is_active", "subscribed_at", "unsubscribed_at")
        }),
        ("Activity", {
            "fields": ("last_newsletter_sent",)
        }),
    )


@admin.register(NewsletterEmail)
class NewsletterEmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at", "total_recipients", "open_count", "click_count")
    list_filter = ("sent_at", "total_recipients")
    search_fields = ("subject", "content")
    readonly_fields = ("sent_at", "total_recipients", "open_count", "click_count")
    filter_horizontal = ("articles",)

