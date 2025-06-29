"""
Email service for sending summary reports.
"""

import smtplib
import logging
from datetime import datetime
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_summary(
        self,
        recipient_emails: List[str],
        subject: str,
        summary: str,
        post_count: int,
        monitored_accounts: List[str]
    ) -> bool:
        """Send the summary via email to multiple recipients."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(recipient_emails)
            msg['Subject'] = f"{subject} - {datetime.now().strftime('%Y-%m-%d')}"

            # Create email header
            header = f"""# 🦋 Daily Bluesky Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC  
**Posts analyzed:** {post_count}  
**Monitored accounts:** {', '.join(monitored_accounts)}

---
"""

            # Combine header with AI summary
            full_markdown = header + summary + "\n\n---\n*This summary was generated automatically by Bluesky Summary Newsletter.*"
            
            # Convert markdown to HTML for better email rendering
            html_body = markdown.markdown(full_markdown, extensions=['extra', 'codehilite'])
            
            # Send only HTML version to avoid duplication
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_emails, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(recipient_emails)} recipients: {', '.join(recipient_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False