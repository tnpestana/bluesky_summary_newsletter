"""
Bluesky API client for fetching user posts.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from atproto import Client

logger = logging.getLogger(__name__)

class BlueskyClient:
    def __init__(self, username: str, password: str):
        self.client = Client()
        self.client.login(username, password)
        logger.info(f"Logged into Bluesky as {username}")

    def fetch_user_posts(self, handle: str, hours_lookback: int, max_posts: int) -> List[Dict[str, Any]]:
        """Fetch posts for a specific user from the last N hours."""
        try:
            logger.info(f"Fetching posts for {handle}")
            
            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours_lookback)
            
            # Get user profile
            profile = self.client.get_profile(handle)
            
            # Fetch user's posts
            posts_response = self.client.get_author_feed(
                actor=handle,
                limit=max_posts
            )
            
            # Filter posts by time
            filtered_posts = []
            for item in posts_response.feed:
                post = item.post
                post_time = datetime.fromisoformat(post.record.created_at.replace('Z', '+00:00'))
                
                if start_time <= post_time <= end_time:
                    filtered_posts.append({
                        'text': post.record.text,
                        'created_at': post.record.created_at,
                        'author': post.author.display_name or post.author.handle,
                        'uri': post.uri
                    })
            
            logger.info(f"Fetched {len(filtered_posts)} posts for {handle}")
            return filtered_posts
            
        except Exception as e:
            logger.error(f"Error fetching posts for {handle}: {str(e)}")
            return []

    def fetch_all_posts(self, handles: List[str], hours_lookback: int, max_posts: int) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch posts for all specified users."""
        all_posts = {}
        
        for handle in handles:
            posts = self.fetch_user_posts(handle, hours_lookback, max_posts)
            all_posts[handle] = posts
        
        return all_posts