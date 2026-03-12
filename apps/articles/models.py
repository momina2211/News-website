"""Articles app models"""
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending Review"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    summary = models.TextField(max_length=500, help_text="Brief summary shown in article cards")
    content = models.TextField()
    featured_image = models.ImageField(upload_to="articles/%Y/%m/", blank=True, null=True)
    featured_image_caption = models.CharField(max_length=200, blank=True)

    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = models.ManyToManyField(
        "tags.Tag",
        blank=True,
        related_name="articles",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    rejection_reason = models.TextField(blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to="og/", blank=True, null=True)
    
    # AI & Analytics fields
    ai_summary = models.TextField(blank=True, help_text="AI-generated summary of the article")
    ai_summary_generated_at = models.DateTimeField(null=True, blank=True)
    trending_score = models.FloatField(default=0, db_index=True)
    last_trending_update = models.DateTimeField(null=True, blank=True)
    reading_time_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["author"]),
            models.Index(fields=["category"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["trending_score"]),
            models.Index(fields=["status", "published_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.meta_description and self.summary:
            self.meta_description = self.summary[:160]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("articles:article_detail", kwargs={"slug": self.slug})

    def increment_views(self):
        Article.objects.filter(pk=self.pk).update(view_count=models.F("view_count") + 1)

    def get_related_articles(self, count=4):
        related = Article.objects.filter(
            status=self.Status.PUBLISHED,
            category=self.category,
        ).exclude(pk=self.pk).order_by("-published_at")[:count]
        if related.count() < count:
            tag_ids = self.tags.values_list("id", flat=True)
            extra = Article.objects.filter(
                status=self.Status.PUBLISHED,
                tags__in=tag_ids,
            ).exclude(pk=self.pk).exclude(
                pk__in=related.values_list("id", flat=True)
            ).distinct().order_by("-published_at")[: count - related.count()]
            from itertools import chain
            return list(chain(related, extra))
        return related

    def can_be_edited_by(self, user):
        if user.is_admin_user or user.is_superuser:
            return True
        if user == self.author and self.status in (self.Status.DRAFT, self.Status.REJECTED):
            return True
        if user.is_editor:
            return True
        return False

    def can_be_published_by(self, user):
        return user.is_editor or user.is_admin_user

    @property
    def reading_time(self):
        if self.reading_time_minutes:
            return self.reading_time_minutes
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    # --- Workflow transitions ---
    def submit_for_review(self, user):
        if user != self.author and not user.is_editor:
            raise PermissionError("Only the author can submit for review.")
        if self.status not in (self.Status.DRAFT, self.Status.REJECTED):
            raise ValueError("Only draft or rejected articles can be submitted for review.")
        self.status = self.Status.PENDING_REVIEW
        self.save(update_fields=["status", "updated_at"])

    def publish(self, user):
        if not self.can_be_published_by(user):
            raise PermissionError("You do not have permission to publish articles.")
        self.status = self.Status.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at", "updated_at"])

    def reject(self, user, reason=""):
        if not user.is_editor and not user.is_admin_user:
            raise PermissionError("Only editors can reject articles.")
        self.status = self.Status.REJECTED
        self.rejection_reason = reason
        self.save(update_fields=["status", "rejection_reason", "updated_at"])

    def revert_to_draft(self, user):
        if user != self.author and not user.is_editor:
            raise PermissionError("Not allowed.")
        self.status = self.Status.DRAFT
        self.save(update_fields=["status", "updated_at"])


class ArticleLike(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="liked_articles")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "user")
        verbose_name = "Article Like"

