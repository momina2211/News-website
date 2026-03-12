"""Admin configuration for analytics app"""
from django.contrib import admin
from .models import ArticleView, UserInteraction, UserInterest


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "ip_address", "viewed_at")
    list_filter = ("viewed_at", "user", "article")
    search_fields = ("article__title", "user__username", "ip_address")
    readonly_fields = ("viewed_at", "user_agent")
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "interaction_type", "created_at")
    list_filter = ("interaction_type", "created_at", "user")
    search_fields = ("user__username", "article__title")
    readonly_fields = ("created_at",)


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "tag", "weight", "updated_at")
    list_filter = ("weight", "updated_at", "category")
    search_fields = ("user__username", "category__name", "tag__name")
    readonly_fields = ("updated_at",)

