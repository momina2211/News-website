"""Comments admin"""
from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "is_approved", "is_spam", "created_at")
    list_filter = ("is_approved", "is_spam", "created_at")
    search_fields = ("content", "user__username", "article__title")
    actions = ["approve_comments", "mark_spam"]
    readonly_fields = ("created_at", "updated_at")

    @admin.action(description="Approve selected comments")
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True, is_spam=False)
        self.message_user(request, f"{updated} comment(s) approved.")

    @admin.action(description="Mark as spam")
    def mark_spam(self, request, queryset):
        updated = queryset.update(is_spam=True, is_approved=False)
        self.message_user(request, f"{updated} comment(s) marked as spam.")

