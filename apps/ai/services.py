"""AI Summary Service"""
import os
import json
from typing import Optional
import requests
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class AISummaryService:
    """Generate AI summaries for articles"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_summary(self, article, max_sentences: int = 3) -> Optional[str]:
        """
        Generate AI summary for an article
        
        Args:
            article: Article model instance
            max_sentences: Maximum sentences in summary
            
        Returns:
            Generated summary or None if API fails
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return None

        try:
            # Prepare content
            text = f"{article.title}\n\n{article.content}"
            
            # Call OpenAI API
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
                            "content": f"Generate a concise summary of the article in exactly {max_sentences} sentences. Make it informative and engaging.",
                        },
                        {
                            "role": "user",
                            "content": text,
                        },
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150,
                },
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"].strip()
                return summary
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in generate_summary: {str(e)}")
            return None

    def regenerate_summary(self, article) -> bool:
        """Regenerate summary for existing article"""
        summary = self.generate_summary(article)
        if summary:
            article.ai_summary = summary
            article.ai_summary_generated_at = timezone.now()
            article.save(update_fields=["ai_summary", "ai_summary_generated_at"])
            return True
        return False

    def auto_generate_on_publish(self, article) -> None:
        """Automatically generate summary when article is published"""
        if not article.ai_summary and article.status == "published":
            self.regenerate_summary(article)

