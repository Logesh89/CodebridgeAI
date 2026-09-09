"""Email service for OTP and notifications."""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    async def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        current_settings = get_settings()
        if not current_settings.smtp_user or not current_settings.smtp_password:
            logger.warning("SMTP not configured. Email to %s: %s", to_email, subject)
            logger.info("Email body: %s", html_body)
            return True

        message = MIMEMultipart("alternative")
        message["From"] = current_settings.smtp_from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname=current_settings.smtp_host,
                port=current_settings.smtp_port,
                username=current_settings.smtp_user,
                password=current_settings.smtp_password,
                start_tls=current_settings.smtp_tls,
            )
            logger.info("Real email successfully sent via Gmail SMTP to %s", to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, e)
            return False

    async def send_otp(self, to_email: str, otp: str) -> bool:
        subject = "Your CodeBridge AI OTP"
        body = f"""
        <html><body>
        <h2>CodeBridge AI</h2>
        <p>Your OTP verification code is:</p>
        <h1 style="letter-spacing: 8px;">{otp}</h1>
        <p>This code expires in {settings.otp_expire_minutes} minutes.</p>
        </body></html>
        """
        return await self.send_email(to_email, subject, body)

    async def send_password_reset(self, to_email: str, reset_link: str) -> bool:
        subject = "Password Reset - CodeBridge AI"
        body = f"""
        <html><body>
        <h2>Password Reset - CodeBridge AI</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        </body></html>
        """
        return await self.send_email(to_email, subject, body)

    async def send_notification(self, to_email: str, title: str, message: str) -> bool:
        subject = f"CodeBridge AI - {title}"
        body = f"<html><body><h2>{title}</h2><p>{message}</p></body></html>"
        return await self.send_email(to_email, subject, body)
