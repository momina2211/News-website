"""Management command to send newsletter digest"""
from django.core.management.base import BaseCommand
from apps.newsletter.services import NewsletterService


class Command(BaseCommand):
    help = "Send weekly newsletter digest to subscribers"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("📧 Sending newsletter..."))
        
        stats = NewsletterService.send_digest()
        
        self.stdout.write(self.style.SUCCESS(
            f"✅ Sent to: {stats['sent']} subscribers"
        ))
        if stats['errors']:
            self.stdout.write(self.style.ERROR(
                f"⚠️  Errors: {stats['errors']}"
            ))
        
        subscriber_count = NewsletterService.get_subscriber_count()
        self.stdout.write(self.style.WARNING(
            f"📊 Active subscribers: {subscriber_count}"
        ))

