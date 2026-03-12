"""Tags admin"""
from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "article_count", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

