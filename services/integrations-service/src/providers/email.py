"""Email integration provider using SMTP."""
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import aiosmtplib

from finops_common import get_logger

from .base import IntegrationProvider, ProviderResponse

logger = get_logger(__name__)


class EmailProvider(IntegrationProvider):
    """Email provider using SMTP (supports Mailhog for local development)."""

    def __init__(self, config: Dict[str, Any], credentials: Optional[Dict[str, Any]] = None):
        """Initialize email provider."""
        super().__init__(config, credentials)
        self.smtp_host = config.get("smtp_host", "localhost")
        self.smtp_port = config.get("smtp_port", 1025)  # Mailhog default
        self.use_tls = config.get("use_tls", False)
        self.use_ssl = config.get("use_ssl", False)
        self.from_email = config.get("from_email", "finops@example.com")
        self.from_name = config.get("from_name", "FinOps Platform")
        
        # Authentication (optional for Mailhog)
        self.username = credentials.get("username") if credentials else None
        self.password = credentials.get("password") if credentials else None

    async def send(self, payload: Dict[str, Any]) -> ProviderResponse:
        """Send email via SMTP."""
        start_time = time.time()
        
        try:
            # Extract email fields from payload
            to_emails = payload.get("to", [])
            if isinstance(to_emails, str):
                to_emails = [to_emails]
            
            cc_emails = payload.get("cc", [])
            if isinstance(cc_emails, str):
                cc_emails = [cc_emails]
            
            bcc_emails = payload.get("bcc", [])
            if isinstance(bcc_emails, str):
                bcc_emails = [bcc_emails]
            
            subject = payload.get("subject", "FinOps Notification")
            body_text = payload.get("body", "")
            body_html = payload.get("body_html")
            
            if not to_emails:
                return ProviderResponse(
                    success=False,
                    error_message="No recipient email addresses provided"
                )
            
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = ", ".join(to_emails)
            if cc_emails:
                msg["Cc"] = ", ".join(cc_emails)
            msg["Subject"] = subject
            
            # Attach text body
            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            
            # Attach HTML body if provided
            if body_html:
                msg.attach(MIMEText(body_html, "html"))
            
            # Send email
            all_recipients = to_emails + cc_emails + bcc_emails
            
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
                start_tls=self.use_ssl and not self.use_tls,
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Email sent to {len(all_recipients)} recipients via {self.smtp_host}:{self.smtp_port}")
            
            return ProviderResponse(
                success=True,
                response_data={
                    "recipients": all_recipients,
                    "subject": subject,
                    "from": self.from_email
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Email send error: {e}")
            return ProviderResponse(
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    async def verify(self) -> ProviderResponse:
        """Verify SMTP server is reachable."""
        try:
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
                start_tls=self.use_ssl and not self.use_tls,
                timeout=10
            ) as smtp:
                # Just connect and disconnect
                await smtp.connect()
                
            return ProviderResponse(
                success=True,
                response_data={"smtp_host": self.smtp_host, "smtp_port": self.smtp_port}
            )
        except Exception as e:
            return ProviderResponse(
                success=False,
                error_message=f"SMTP verification failed: {str(e)}"
            )

    async def test(self, payload: Optional[Dict[str, Any]] = None) -> ProviderResponse:
        """Test email with sample payload."""
        test_payload = payload or {
            "to": ["test@example.com"],
            "subject": "Test Email from FinOps Platform",
            "body": "This is a test email to verify SMTP integration is working correctly.",
            "body_html": "<h2>Test Email</h2><p>This is a test email to verify SMTP integration is working correctly.</p>"
        }
        
        return await self.send(test_payload)
