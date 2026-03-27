from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings


class EmailClient:
    """Client for sending transactional emails via SMTP"""

    def __init__(self) -> None:
        """Initialize EmailClient with SMTP settings from config"""
        self.host = settings.email.host
        self.port = settings.email.port
        self.username = settings.email.username
        self.password = settings.email.password

    async def verify(self, recipient: str, token: str) -> None:
        """Send email verification token to user"""
        message = self._build(
            recipient=recipient,
            subject="Verify your email",
            body=f"Your verification token: {token}",
        )
        await self._send(recipient, message)

    async def reset(self, recipient: str, token: str) -> None:
        """Send password reset token to user"""
        message = self._build(
            recipient=recipient,
            subject="Reset your password",
            body=f"Your password reset token: {token}",
        )
        await self._send(recipient, message)

    def _build(self, recipient: str, subject: str, body: str) -> MIMEText:
        """Build a MIME email message"""
        message = MIMEText(body)
        message["From"] = self.username
        message["To"] = recipient
        message["Subject"] = subject
        return message

    async def _send(self, recipient: str, message: MIMEText) -> None:
        """Send a MIME message via SMTP."""
        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            start_tls=True,
        )
