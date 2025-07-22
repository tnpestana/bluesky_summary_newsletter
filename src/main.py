#!/usr/bin/env python3
"""
Bluesky Summary Newsletter
Fetches posts from configured users and sends AI-generated summaries via email.
"""

import logging
from config_loader import ConfigLoader
from bluesky_client import BlueskyClient
from ai_summarizer import AISummarizer
from email_sender import EmailSender

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlueskySummaryNewsletter:
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        self.config_loader = ConfigLoader(config_path)
        
        # Get configuration sections
        bluesky_config = self.config_loader.get_bluesky_config()
        ai_config = self.config_loader.get_ai_config()
        email_config = self.config_loader.get_email_config()
        self.settings = self.config_loader.get_settings()
        self.bluesky_users = self.config_loader.get_bluesky_users()
        
        # Initialize components
        self.bluesky_client = BlueskyClient(
            bluesky_config["username"],
            bluesky_config["password"]
        )
        
        self.ai_summarizer = AISummarizer(
            ai_config["provider"],
            ai_config["models"],
            ai_config.get("base_url")
        )
        
        self.email_sender = EmailSender(
            email_config["smtp_server"],
            email_config["smtp_port"],
            email_config["sender_email"],
            email_config["sender_password"]
        )
        
        self.email_config = email_config

    def run(self):
        """Main execution method."""
        logger.info("Starting Bluesky Summary Newsletter...")
        
        # Fetch posts
        logger.info("Fetching posts from Bluesky...")
        posts_data = self.bluesky_client.fetch_all_posts(
            self.bluesky_users,
            self.settings["hours_lookback"],
            self.settings["max_posts_per_user"]
        )
        
        # Count total posts
        total_posts = sum(len(posts) for posts in posts_data.values())
        logger.info(f"Total posts fetched: {total_posts}")
        
        # Generate summary (even if no posts found)
        if total_posts == 0:
            logger.info("No posts found. Generating empty summary email...")
            summary = "No new posts were found from the monitored accounts in the last {} hours.".format(self.settings["hours_lookback"])
        else:
            logger.info("Generating AI summary...")
            summary = self.ai_summarizer.generate_summary(posts_data)
        
        # Send email
        logger.info("Sending email...")
        success = self.email_sender.send_summary(
            self.email_config["recipient_emails"],
            self.email_config["subject"],
            summary,
            total_posts,
            self.bluesky_users
        )
        
        if success:
            logger.info("Bluesky Summary Newsletter completed successfully!")
        else:
            logger.error("Failed to send email. Newsletter incomplete.")
            raise Exception("Email sending failed")

if __name__ == "__main__":
    newsletter = BlueskySummaryNewsletter()
    newsletter.run()