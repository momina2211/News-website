"""AI Headline Generation Service"""
import os
import requests
import json
import logging
from typing import List, Dict
from apps.ai.models import AIHeadlineSuggestion

logger = logging.getLogger(__name__)


class AIHeadlineService:
    """Generate SEO-optimized headlines"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_headlines(self, article) -> List[Dict[str, str]]:
        """
        Generate headline variations
        
        Returns:
            List of dicts with full_headline, short_headline, social_headline
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
                            "content": """Generate 5 sets of SEO-optimized headlines. For each set, provide:
1. Full headline (60 chars max)
2. Short headline (30 chars max)
3. Social media headline (100 chars max, engaging tone)

Format as JSON array with objects containing: full, short, social""",
                        },
                        {
                            "role": "user",
                            "content": text,
                        },
                    ],
                    "temperature": 0.8,
                    "max_tokens": 500,
                },
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Extract JSON from response
                try:
                    # Try to find JSON array in response
                    start = content.find('[')
                    end = content.rfind(']') + 1
                    if start >= 0 and end > start:
                        json_str = content[start:end]
                        headlines = json.loads(json_str)
                        
                        # Normalize keys
                        normalized = []
                        for h in headlines:
                            normalized.append({
                                "full_headline": h.get("full", h.get("Full", ""))[:300],
                                "short_headline": h.get("short", h.get("Short", ""))[:100],
                                "social_headline": h.get("social", h.get("Social", ""))[:150],
                            })
                        return normalized[:5]
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from headline response")
                    return []
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error in generate_headlines: {str(e)}")
            return []

    def save_suggestions(self, article) -> int:
        """Generate and save headline suggestions"""
        headlines = self.generate_headlines(article)
        count = 0

        for idx, h in enumerate(headlines, 1):
            if all([h.get("full_headline"), h.get("short_headline"), h.get("social_headline")]):
                AIHeadlineSuggestion.objects.create(
                    article=article,
                    full_headline=h["full_headline"],
                    short_headline=h["short_headline"],
                    social_headline=h["social_headline"],
                    relevance_score=1.0 - (idx * 0.1),  # Decreasing relevance
                )
                count += 1

        return count

    def use_headline(self, article, headline_id: int) -> bool:
        """Apply selected headline to article"""
        try:
            suggestion = AIHeadlineSuggestion.objects.get(id=headline_id, article=article)
            article.title = suggestion.full_headline
            article.meta_description = suggestion.social_headline[:160]
            article.save(update_fields=["title", "meta_description", "updated_at"])
            
            # Mark as used
            suggestion.was_used = True
            suggestion.save(update_fields=["was_used"])
            
            return True
        except AIHeadlineSuggestion.DoesNotExist:
            return False

