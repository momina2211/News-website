"""Accounts app models"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Extended user model with role-based permissions."""

    class Role(models.TextChoices):
        READER = "reader", "Reader"
        AUTHOR = "author", "Author"
        EDITOR = "editor", "Editor"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    def get_absolute_url(self):
        return reverse("articles:author_articles", kwargs={"username": self.username})

    @property
    def is_author(self):
        return self.role in (self.Role.AUTHOR, self.Role.EDITOR, self.Role.ADMIN) or self.is_staff

    @property
    def is_editor(self):
        return self.role in (self.Role.EDITOR, self.Role.ADMIN) or self.is_staff

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        initials = (self.first_name[:1] + self.last_name[:1]).upper() or self.username[:2].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=3B82F6&color=fff&size=128"

