"""Articles admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Article, ArticleLike


class ArticleLikeInline(admin.TabularInline):
    model = ArticleLike
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title", "author", "category", "status",
        "view_count", "like_count", "is_featured", "published_at", "created_at",
    )
    list_filter = ("status", "is_featured", "category", "created_at", "published_at")
    search_fields = ("title", "summary", "content", "author__username", "author__email")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("view_count", "like_count", "created_at", "updated_at", "preview_image")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    filter_horizontal = ("tags",)
    inlines = [ArticleLikeInline]
    actions = ["make_published", "make_draft", "mark_featured"]

    fieldsets = (
        ("Content", {
            "fields": ("title", "slug", "summary", "content")
        }),
        ("Media", {
            "fields": ("featured_image", "preview_image", "featured_image_caption", "og_image")
        }),
        ("Classification", {
            "fields": ("author", "category", "tags")
        }),
        ("Workflow", {
            "fields": ("status", "rejection_reason", "is_featured")
        }),
        ("SEO", {
            "fields": ("meta_description",),
            "classes": ("collapse",),
        }),
        ("Stats", {
            "fields": ("view_count", "like_count", "published_at", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def preview_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="200" style="border-radius:4px"/>', obj.featured_image.url)
        return "No image"
    preview_image.short_description = "Preview"

    @admin.action(description="Publish selected articles")
    def make_published(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status="pending_review").update(
            status="published", published_at=timezone.now()
        )
        self.message_user(request, f"{updated} article(s) published.")

    @admin.action(description="Revert to draft")
    def make_draft(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} article(s) moved to draft.")

    @admin.action(description="Toggle featured")
    def mark_featured(self, request, queryset):
        for article in queryset:
            article.is_featured = not article.is_featured
            article.save(update_fields=["is_featured"])
        self.message_user(request, "Featured status toggled.")

