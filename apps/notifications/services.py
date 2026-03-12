"""Notification Service"""
from apps.notifications.models import Notification
from apps.articles.models import Article
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Manage user notifications"""

    @staticmethod
    def notify_comment_reply(comment, parent_comment) -> None:
        """Notify user when comment is replied to"""
        if comment.user_id == parent_comment.user_id:
            return  # Don't notify self
        
        Notification.objects.create(
            user=parent_comment.user,
            notification_type="comment_reply",
            message=f"{comment.user.get_full_name()} replied to your comment",
            article=comment.article,
            related_user=comment.user,
            url=comment.article.get_absolute_url()
        )

    @staticmethod
    def notify_article_approved(article) -> None:
        """Notify author when article is approved"""
        Notification.objects.create(
            user=article.author,
            notification_type="article_approved",
            message=f"Your article '{article.title}' has been approved!",
            article=article,
            url=article.get_absolute_url()
        )

    @staticmethod
    def notify_article_rejected(article, rejection_reason: str = "") -> None:
        """Notify author when article is rejected"""
        message = f"Your article '{article.title}' was rejected"
        if rejection_reason:
            message += f": {rejection_reason}"
        
        Notification.objects.create(
            user=article.author,
            notification_type="article_rejected",
            message=message,
            article=article,
            url=article.get_absolute_url()
        )

    @staticmethod
    def notify_new_article_from_followed(article) -> None:
        """Notify followers when author publishes new article"""
        from apps.notifications.models import FollowAuthor
        
        followers = FollowAuthor.objects.filter(
            author=article.author
        ).values_list("user_id", flat=True)
        
        notifications = [
            Notification(
                user_id=follower_id,
                notification_type="new_follower_article",
                message=f"{article.author.get_full_name()} published '{article.title}'",
                article=article,
                related_user=article.author,
                url=article.get_absolute_url()
            )
            for follower_id in followers
        ]
        
        Notification.objects.bulk_create(notifications, ignore_conflicts=True)

    @staticmethod
    def notify_article_liked(article, user) -> None:
        """Notify author when article is liked"""
        if user.id == article.author.id:
            return  # Don't notify self
        
        Notification.objects.create(
            user=article.author,
            notification_type="like",
            message=f"{user.get_full_name()} liked your article '{article.title}'",
            article=article,
            related_user=user,
            url=article.get_absolute_url()
        )

    @staticmethod
    def get_unread_count(user) -> int:
        """Get count of unread notifications"""
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def get_recent_notifications(user, limit: int = 10) -> list:
        """Get recent notifications for user"""
        return list(
            Notification.objects.filter(user=user).order_by("-created_at")[:limit]
        )

    @staticmethod
    def mark_all_as_read(user) -> int:
        """Mark all user notifications as read"""
        from django.utils import timezone
        
        unread = Notification.objects.filter(user=user, is_read=False)
        count = unread.count()
        
        if count > 0:
            unread.update(is_read=True, read_at=timezone.now())
        
        return count

