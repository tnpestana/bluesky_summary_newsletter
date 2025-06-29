"""
Email service for sending summary reports.
"""

import smtplib
import logging
from datetime import datetime
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

            body = f"""
Daily Bluesky Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total posts analyzed: {post_count}
Monitored accounts: {', '.join(monitored_accounts)}

{summary}

---
This summary was generated automatically by Bluesky Summary Newsletter.
            """

            msg.attach(MIMEText(body, 'plain'))

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