"""AI Tag Recommendation Service"""
import os
import requests
import logging
from typing import List, Dict
from apps.ai.models import AITagSuggestion
from apps.tags.models import Tag

logger = logging.getLogger(__name__)


class AITagRecommendationService:
    """AI-powered tag recommendation engine"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def get_tag_recommendations(self, article, limit: int = 10) -> List[str]:
        """
        Get tag recommendations for an article
        
        Args:
            article: Article model instance
            limit: Maximum number of tags to recommend
            
        Returns:
            List of recommended tag names
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return []

        try:
            text = f"Title: {article.title}\n\nContent: {article.content[:2000]}"
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": f"Analyze this article and suggest {limit} relevant tags. Return only tag names, one per line, without numbers or symbols.",
                        },
                        {
                            "role": "user",
                            "content": text,
                        },
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200,
                },
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                tags = [tag.strip().lower() for tag in content.split('\n') if tag.strip()]
                return tags[:limit]
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error in get_tag_recommendations: {str(e)}")
            return []

    def apply_recommendations(self, article, confidence_threshold: float = 0.5) -> Dict[str, int]:
        """
        Get recommendations, create new tags, and save suggestions
        
        Returns:
            Dict with counts of approved/rejected tags
        """
        tags = self.get_tag_recommendations(article)
        stats = {"created": 0, "suggested": 0, "existing": 0}

        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={"slug": tag_name.lower().replace(" ", "-")}
            )
            
            if created:
                stats["created"] += 1
            else:
                stats["existing"] += 1

            # Create suggestion record
            AITagSuggestion.objects.get_or_create(
                article=article,
                tag=tag,
                defaults={
                    "confidence_score": confidence_threshold,
                }
            )
            stats["suggested"] += 1

        return stats

    def auto_suggest_tags(self, article) -> None:
        """Automatically suggest tags for unpublished articles"""
        if article.status in ["draft", "pending_review"]:
            self.apply_recommendations(article)

