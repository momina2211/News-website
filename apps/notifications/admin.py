"""Admin configuration for notifications app"""
from django.contrib import admin
from .models import Notification, FollowAuthor


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "message", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at", "user")
    search_fields = ("user__username", "message", "article__title")
    readonly_fields = ("created_at", "read_at")
    fieldsets = (
        ("User & Type", {
            "fields": ("user", "notification_type")
        }),
        ("Content", {
            "fields": ("message", "article", "related_user", "url")
        }),
        ("Status", {
            "fields": ("is_read", "created_at", "read_at")
        }),
    )


@admin.register(FollowAuthor)
class FollowAuthorAdmin(admin.ModelAdmin):
    list_display = ("user", "author", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("user__username", "author__username")
    readonly_fields = ("created_at",)

