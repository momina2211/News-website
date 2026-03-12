from django import template
from ..models import Category

register = template.Library()


@register.simple_tag
def get_categories():
    return Category.objects.all()


@register.filter
def reading_time(content):
    words = len(str(content).split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"
