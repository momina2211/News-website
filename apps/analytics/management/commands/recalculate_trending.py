"""Management command to recalculate trending scores"""
from django.core.management.base import BaseCommand
from apps.analytics.trending_service import TrendingService


class Command(BaseCommand):
    help = "Recalculate trending scores for all published articles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Only recalculate for articles from last N days (default: 30)"
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔄 Starting trending calculation..."))
        
        stats = TrendingService.recalculate_all_trending()
        
        self.stdout.write(self.style.SUCCESS(
            f"✅ Updated: {stats['updated']} articles"
        ))
        if stats['errors']:
            self.stdout.write(self.style.ERROR(
                f"⚠️  Errors: {stats['errors']}"
            ))

