"""
cbms_api/services/notification.py
Webhook + email notification service for alarm escalation.

Supports three delivery channels, enabled via environment variables:
  WEBHOOK_URL        — generic HTTP POST webhook (Slack, Teams, PagerDuty, etc.)
  SMTP_HOST          — SMTP email relay
  PAGERDUTY_KEY      — PagerDuty Events API v2 routing key

All channels are fire-and-forget (async).  Failures are logged but do NOT
raise — operator workflows must not be blocked by notification failures.
"""

from __future__ import annotations

import os
import json
import asyncio
import logging
import smtplib
from datetime import datetime, UTC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class AlarmNotificationService:
    """
    Delivers alarm escalation notifications through configured channels.

    Instantiate once (singleton pattern) and call notify_escalation().
    """

    def __init__(self) -> None:
        self.webhook_url    = os.getenv("WEBHOOK_URL", "")
        self.smtp_host      = os.getenv("SMTP_HOST", "")
        self.smtp_port      = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user      = os.getenv("SMTP_USER", "")
        self.smtp_password  = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from      = os.getenv("SMTP_FROM", "noreply@carbonize.in")
        self.smtp_to        = os.getenv("ALARM_EMAIL_TO", "")
        self.pagerduty_key  = os.getenv("PAGERDUTY_KEY", "")
        self.pagerduty_url  = "https://events.pagerduty.com/v2/enqueue"
        self.app_name       = os.getenv("APP_NAME", "Carbonize CBMS")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def notify_escalation(
        self,
        *,
        alert_id: str,
        plant_id: str,
        plant_name: str = "",
        severity: str = "HIGH",
        title: str = "",
        message: str = "",
        actor: str = "system",
        escalated_at: Optional[datetime] = None,
    ) -> dict[str, list[str]]:
        """
        Fire all configured channels concurrently.
        Returns {'sent': [...], 'failed': [...]} channel names.
        """
        ts = escalated_at or datetime.now(UTC)
        payload = {
            "alert_id":   alert_id,
            "plant_id":   plant_id,
            "plant_name": plant_name,
            "severity":   severity,
            "title":      title or f"[{severity}] Alarm escalated at {plant_name}",
            "message":    message,
            "actor":      actor,
            "escalated_at": ts.isoformat(),
        }

        tasks = []
        labels = []

        if self.webhook_url:
            tasks.append(self._send_webhook(payload))
            labels.append("webhook")

        if self.smtp_host and self.smtp_to:
            tasks.append(self._send_email(payload))
            labels.append("email")

        if self.pagerduty_key:
            tasks.append(self._send_pagerduty(payload))
            labels.append("pagerduty")

        if not tasks:
            logger.info(
                "No notification channels configured. Set WEBHOOK_URL / SMTP_HOST / PAGERDUTY_KEY."
            )
            return {"sent": [], "failed": [], "skipped": ["no_channels_configured"]}

        results = await asyncio.gather(*tasks, return_exceptions=True)

        sent, failed = [], []
        for label, result in zip(labels, results):
            if isinstance(result, Exception):
                logger.error("Notification channel '%s' failed: %s", label, result)
                failed.append(label)
            else:
                sent.append(label)

        return {"sent": sent, "failed": failed}

    # ------------------------------------------------------------------
    # Channel implementations
    # ------------------------------------------------------------------

    async def _send_webhook(self, payload: dict) -> None:
        """POST JSON payload to the configured webhook URL."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                self.webhook_url,
                json={
                    "text": payload["title"],
                    "attachments": [
                        {
                            "color":  self._severity_color(payload["severity"]),
                            "fields": [
                                {"title": "Plant",     "value": payload["plant_name"], "short": True},
                                {"title": "Alert ID",  "value": payload["alert_id"],  "short": True},
                                {"title": "Severity",  "value": payload["severity"],  "short": True},
                                {"title": "Escalated", "value": payload["escalated_at"], "short": True},
                                {"title": "Message",   "value": payload["message"],   "short": False},
                            ],
                        }
                    ],
                },
            )
            resp.raise_for_status()

    async def _send_email(self, payload: dict) -> None:
        """Send HTML email via SMTP (runs in thread pool to avoid blocking)."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = payload["title"]
        msg["From"]    = self.smtp_from
        msg["To"]      = self.smtp_to

        html = f"""
        <html><body>
        <h2 style="color:{self._severity_color(payload['severity'])}">
            {payload['title']}
        </h2>
        <table border="1" cellpadding="6">
          <tr><th>Plant</th><td>{payload['plant_name']}</td></tr>
          <tr><th>Alert ID</th><td>{payload['alert_id']}</td></tr>
          <tr><th>Severity</th><td>{payload['severity']}</td></tr>
          <tr><th>Escalated by</th><td>{payload['actor']}</td></tr>
          <tr><th>Timestamp</th><td>{payload['escalated_at']}</td></tr>
          <tr><th>Details</th><td>{payload['message']}</td></tr>
        </table>
        <p><em>Sent by {self.app_name}</em></p>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._smtp_send, msg)

    def _smtp_send(self, msg: MIMEMultipart) -> None:
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_from, self.smtp_to.split(","), msg.as_string())

    async def _send_pagerduty(self, payload: dict) -> None:
        """Trigger a PagerDuty incident via Events API v2."""
        severity_map = {
            "CRITICAL": "critical",
            "HIGH": "error",
            "MEDIUM": "warning",
            "LOW": "info",
        }
        pd_payload = {
            "routing_key":  self.pagerduty_key,
            "event_action": "trigger",
            "dedup_key":    payload["alert_id"],
            "payload": {
                "summary":   payload["title"],
                "source":    payload["plant_name"] or payload["plant_id"],
                "severity":  severity_map.get(payload["severity"].upper(), "warning"),
                "component": "CBMS Alarm",
                "custom_details": {
                    "alert_id":    payload["alert_id"],
                    "plant_id":    payload["plant_id"],
                    "message":     payload["message"],
                    "escalated_by": payload["actor"],
                },
            },
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(self.pagerduty_url, json=pd_payload)
            resp.raise_for_status()

    @staticmethod
    def _severity_color(severity: str) -> str:
        return {
            "CRITICAL": "#FF0000",
            "HIGH":     "#FF6600",
            "MEDIUM":   "#FFCC00",
            "LOW":      "#00CC00",
        }.get(severity.upper(), "#666666")


# Singleton instance
notification_service = AlarmNotificationService()
