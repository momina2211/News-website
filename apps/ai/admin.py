"""Admin configuration for AI app"""
from django.contrib import admin
from .models import AITagSuggestion, AIHeadlineSuggestion, AIModel


@admin.register(AITagSuggestion)
class AITagSuggestionAdmin(admin.ModelAdmin):
    list_display = ("article", "tag", "confidence_score", "was_approved", "suggested_at")
    list_filter = ("was_approved", "confidence_score", "suggested_at")
    search_fields = ("article__title", "tag__name")
    readonly_fields = ("suggested_at", "confidence_score")
    fieldsets = (
        ("Article & Tag", {
            "fields": ("article", "tag")
        }),
        ("Metadata", {
            "fields": ("confidence_score", "was_approved", "suggested_at")
        }),
    )


@admin.register(AIHeadlineSuggestion)
class AIHeadlineSuggestionAdmin(admin.ModelAdmin):
    list_display = ("article", "full_headline", "relevance_score", "was_used", "suggested_at")
    list_filter = ("was_used", "relevance_score", "suggested_at")
    search_fields = ("article__title", "full_headline")
    readonly_fields = ("suggested_at", "relevance_score")
    fieldsets = (
        ("Article", {
            "fields": ("article",)
        }),
        ("Headlines", {
            "fields": ("full_headline", "short_headline", "social_headline")
        }),
        ("Metadata", {
            "fields": ("relevance_score", "was_used", "suggested_at")
        }),
    )


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "is_active", "created_at")
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("name", "model_id")
    readonly_fields = ("created_at",)

