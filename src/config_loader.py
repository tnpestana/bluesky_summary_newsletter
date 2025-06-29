"""
Configuration loader with environment variable support.
"""

import yaml
import os
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        # Load environment variables
        load_dotenv()
        
        with open(config_path, 'r') as file:
            config_content = file.read()
        
        # Replace environment variable placeholders
        config_content = os.path.expandvars(config_content)
        
        self.config = yaml.safe_load(config_content)

    def get_bluesky_config(self):
        """Get Bluesky configuration."""
        return self.config["bluesky"]

    def get_bluesky_users(self):
        """Get list of Bluesky users to monitor."""
        return self.config["bluesky_users"]

    def get_ai_config(self):
        """Get AI configuration."""
        return self.config["ai"]

    def get_email_config(self):
        """Get email configuration."""
        return self.config["email"]

    def get_settings(self):
        """Get general settings."""
        return self.config["settings"]

    def get_full_config(self):
        """Get the complete configuration."""
        return self.config