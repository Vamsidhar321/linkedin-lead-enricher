"""
Slack integration for notifications
"""

import requests
import logging
from typing import Optional
from datetime import datetime
from .config import config

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Handles Slack notifications for workflow events"""

    def __init__(self, webhook_url: str = None):
        """
        Initialize Slack notifier

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url or config.SLACK_WEBHOOK_URL

    def is_configured(self) -> bool:
        """Check if Slack webhook is configured"""
        return bool(self.webhook_url)

    def send_message(self, message: str, color: str = "#36a64f") -> bool:
        """
        Send a message to Slack

        Args:
            message: Message text
            color: Message color (hex code)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.debug("Slack webhook not configured, skipping notification")
            return False

        payload = {
            "attachments": [
                {
                    "color": color,
                    "text": message,
                    "ts": int(datetime.now().timestamp()),
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Slack notification sent: {message}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

    def notify_started(self, company_count: int = 0, keyword_count: int = 0) -> bool:
        """
        Notify that enrichment workflow has started

        Args:
            company_count: Number of companies to process
            keyword_count: Number of keywords to search

        Returns:
            True if successful
        """
        message = f"🚀 LinkedIn Enrichment Started\n"
        if company_count > 0:
            message += f"Companies: {company_count}\n"
        if keyword_count > 0:
            message += f"Keywords: {keyword_count}\n"

        return self.send_message(message, color="#0099ff")

    def notify_progress(self, stage: str, current: int, total: int) -> bool:
        """
        Notify progress of enrichment workflow

        Args:
            stage: Current stage (e.g., "Extracting posts", "Enriching profiles")
            current: Current count
            total: Total count

        Returns:
            True if successful
        """
        percentage = (current / total * 100) if total > 0 else 0
        message = f"⏳ {stage}: {current}/{total} ({percentage:.1f}%)"

        return self.send_message(message, color="#ffcc00")

    def notify_completed(
        self,
        total_posts: int,
        total_engagements: int,
        unique_people: int,
        download_url: Optional[str] = None
    ) -> bool:
        """
        Notify that enrichment workflow completed

        Args:
            total_posts: Total posts found
            total_engagements: Total engagements found
            unique_people: Total unique people enriched
            download_url: Optional download link for results

        Returns:
            True if successful
        """
        message = f"✅ LinkedIn Enrichment Completed!\n"
        message += f"Posts Found: {total_posts}\n"
        message += f"Engagements: {total_engagements}\n"
        message += f"Unique People: {unique_people}\n"

        if download_url:
            message += f"<{download_url}|Download Results>"

        return self.send_message(message, color="#36a64f")

    def notify_failed(self, error_message: str) -> bool:
        """
        Notify that enrichment workflow failed

        Args:
            error_message: Error description

        Returns:
            True if successful
        """
        message = f"❌ LinkedIn Enrichment Failed\n{error_message}"
        return self.send_message(message, color="#ff0000")

    def notify_error(self, stage: str, error: str) -> bool:
        """
        Notify about an error during processing

        Args:
            stage: Stage where error occurred
            error: Error message

        Returns:
            True if successful
        """
        message = f"⚠️ Error in {stage}: {error}"
        return self.send_message(message, color="#ff9900")
