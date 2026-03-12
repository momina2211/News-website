"""Articles context processor"""
from django.conf import settings


def site_settings_processor(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "NewsHub"),
        "SITE_URL": getattr(settings, "SITE_URL", "http://localhost:8000"),
    }

