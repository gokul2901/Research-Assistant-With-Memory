"""
n8n Webhook Integration and Automation Client.
Dispatches scraping jobs to n8n workflows and validates callback secrets.
"""

from typing import Optional, Dict, Any
import httpx
from src.config.settings import settings
from src.utils.logger import logger


class N8NIntegrationClient:
    def __init__(
        self,
        webhook_url: Optional[str] = settings.N8N_WEBHOOK_URL,
        callback_secret: str = settings.N8N_CALLBACK_SECRET,
        timeout: int = 15
    ):
        self.webhook_url = webhook_url
        self.callback_secret = callback_secret
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        """Returns True if n8n webhook URL is set."""
        return bool(self.webhook_url and self.webhook_url.startswith(("http://", "https://")))

    async def trigger_scraping_workflow(
        self,
        job_id: str,
        source_id: str,
        url: str,
        callback_url: str
    ) -> bool:
        """
        Trigger an n8n webhook workflow to scrape a webpage.
        Payload:
        {
          "job_id": "job_123",
          "source_id": "src_123",
          "url": "https://example.com/article",
          "callback_url": "https://api.example.com/api/v1/ingestion/callback"
        }
        """
        if not self.is_configured:
            logger.debug(f"n8n webhook not configured; fallback to internal scraping engine for {url}")
            return False

        payload = {
            "job_id": job_id,
            "source_id": source_id,
            "url": url,
            "callback_url": callback_url,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Dispatching ingestion job '{job_id}' to n8n webhook at {self.webhook_url}")
                response = await client.post(
                    self.webhook_url, # type: ignore
                    json=payload,
                    headers={"X-N8N-Callback-Secret": self.callback_secret}
                )
                response.raise_for_status()
                logger.info(f"n8n webhook triggered successfully for job '{job_id}'")
                return True
        except Exception as e:
            logger.warning(f"Failed to trigger n8n webhook for job '{job_id}': {e}. Falling back to local scraper.")
            return False

    def verify_callback_secret(self, secret: Optional[str]) -> bool:
        """Verify that incoming callback request provides matching secret header or token."""
        if not secret:
            return False
        return secret.strip() == self.callback_secret.strip()


# Global instance
n8n_client = N8NIntegrationClient()
