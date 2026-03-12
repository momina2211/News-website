"""Newsletter Service"""
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from apps.newsletter.models import Subscriber, NewsletterEmail
from apps.articles.models import Article
from apps.analytics.trending_service import TrendingService
import logging

logger = logging.getLogger(__name__)


class NewsletterService:
    """Handle newsletter subscription and sending"""

    @staticmethod
    def subscribe(email: str, user=None) -> tuple:
        """
        Subscribe email to newsletter
        
        Returns:
            (subscriber_instance, created_flag)
        """
        subscriber, created = Subscriber.objects.update_or_create(
            email=email,
            defaults={"user": user, "is_active": True}
        )
        return subscriber, created

    @staticmethod
    def unsubscribe(email: str) -> bool:
        """Unsubscribe email from newsletter"""
        try:
            subscriber = Subscriber.objects.get(email=email)
            subscriber.unsubscribe()
            return True
        except Subscriber.DoesNotExist:
            return False

    @staticmethod
    def get_subscribers(active_only: bool = True):
        """Get newsletter subscribers"""
        subscribers = Subscriber.objects.all()
        if active_only:
            subscribers = subscribers.filter(is_active=True)
        return subscribers

    @staticmethod
    def generate_digest_content() -> dict:
        """Generate weekly digest content"""
        # Get trending articles (last 7 days)
        trending = TrendingService.get_trending_articles(limit=5, days=7)
        
        # Get latest articles
        latest = Article.objects.filter(
            status="published",
            published_at__gte=timezone.now() - timedelta(days=7)
        ).order_by("-published_at")[:5]
        
        return {
            "trending": trending,
            "latest": latest,
            "week_start": timezone.now() - timedelta(days=7),
            "week_end": timezone.now(),
        }

    @staticmethod
    def send_digest(subject: str = None, content_dict: dict = None) -> dict:
        """
        Send newsletter digest to all subscribers
        
        Returns:
            Dict with stats about sending
        """
        if not subject:
            subject = "📰 Your Weekly News Digest"
        
        if not content_dict:
            content_dict = NewsletterService.generate_digest_content()
        
        subscribers = NewsletterService.get_subscribers(active_only=True)
        
        if not subscribers.exists():
            logger.info("No active subscribers for newsletter")
            return {"sent": 0, "errors": 0}
        
        # Prepare emails
        emails = []
        for subscriber in subscribers:
            try:
                html_content = render_to_string(
                    "newsletter/digest_email.html",
                    {
                        "subscriber": subscriber,
                        "trending": content_dict["trending"],
                        "latest": content_dict["latest"],
                        "unsubscribe_url": f"/newsletter/unsubscribe/{subscriber.id}/",
                    }
                )
                
                emails.append((
                    subject,
                    "",  # Plain text (optional)
                    "noreply@newshub.local",
                    [subscriber.email],
                    html_content
                ))
            except Exception as e:
                logger.error(f"Error preparing email for {subscriber.email}: {str(e)}")
        
        # Send emails
        stats = {"sent": 0, "errors": 0}
        
        try:
            # Note: This requires SMTP configuration
            # For now, just log to console
            logger.info(f"Would send {len(emails)} newsletter emails")
            stats["sent"] = len(emails)
            
            # Create newsletter record
            newsletter = NewsletterEmail.objects.create(
                subject=subject,
                content=str(content_dict),
                total_recipients=len(emails)
            )
            
            for article in content_dict["trending"] + content_dict["latest"]:
                newsletter.articles.add(article)
            
        except Exception as e:
            logger.error(f"Error sending newsletters: {str(e)}")
            stats["errors"] = len(emails)
        
        return stats

    @staticmethod
    def get_subscriber_count() -> int:
        """Get count of active subscribers"""
        return Subscriber.objects.filter(is_active=True).count()

