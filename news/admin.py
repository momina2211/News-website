from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'published_date', 'views_count')
    list_filter = ('status', 'is_featured', 'category', 'published_date')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    actions = ['make_published', 'make_draft', 'make_archived']

    def make_published(self, request, queryset):
        queryset.update(status='published')
    make_published.short_description = 'Mark selected articles as published'

    def make_draft(self, request, queryset):
        queryset.update(status='draft')
    make_draft.short_description = 'Mark selected articles as draft'

    def make_archived(self, request, queryset):
        queryset.update(status='archived')
    make_archived.short_description = 'Mark selected articles as archived'
