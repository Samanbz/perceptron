"""Reddit sourcer implementation using PRAW (Python Reddit API Wrapper)."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import os

try:
    import praw
    from praw.models import Submission
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

from .base import BaseSourcer, SourcedContent


class RedditSourcer(BaseSourcer):
    """
    Sourcer for Reddit posts and comments.
    
    Reddit API Access:
    - Free tier: 100 requests per minute
    - Requires Reddit account and app credentials
    - No credit card needed
    
    Setup:
    1. Create Reddit account at https://www.reddit.com
    2. Go to https://www.reddit.com/prefs/apps
    3. Click "Create App" or "Create Another App"
    4. Choose "script" type
    5. Get client_id, client_secret
    6. Set environment variables or pass as parameters
    """

    def __init__(
        self,
        subreddit: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = 100,
        time_filter: str = "day",  # hour, day, week, month, year, all
        sort_by: str = "hot",  # hot, new, rising, top, controversial
    ):
        """
        Initialize Reddit sourcer.

        Args:
            subreddit: Name of subreddit (without r/)
            client_id: Reddit API client ID (or set REDDIT_CLIENT_ID env var)
            client_secret: Reddit API client secret (or set REDDIT_CLIENT_SECRET env var)
            user_agent: User agent string (or set REDDIT_USER_AGENT env var)
            name: Optional name for this sourcer
            limit: Maximum number of posts to fetch (default: 100)
            time_filter: Time filter for top/controversial (default: day)
            sort_by: Sort method (default: hot)
        """
        super().__init__(name)
        
        if not PRAW_AVAILABLE:
            raise ImportError(
                "praw is not installed. Install it with: pip install praw"
            )
        
        self.subreddit = subreddit
        self.limit = limit
        self.time_filter = time_filter
        self.sort_by = sort_by
        
        # Get credentials from parameters or environment
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent or os.getenv(
            "REDDIT_USER_AGENT", "Perceptron Intelligence Aggregator v1.0"
        )
        
        self.validate_config()
        
        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            check_for_async=False,
        )

    def validate_config(self, **kwargs) -> bool:
        """Validate Reddit sourcer configuration."""
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Reddit API credentials required. Set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET environment variables or pass as parameters. "
                "Get credentials at: https://www.reddit.com/prefs/apps"
            )
        
        if not self.subreddit:
            raise ValueError("subreddit name is required")
        
        valid_sorts = ["hot", "new", "rising", "top", "controversial"]
        if self.sort_by not in valid_sorts:
            raise ValueError(f"sort_by must be one of: {valid_sorts}")
        
        valid_time_filters = ["hour", "day", "week", "month", "year", "all"]
        if self.time_filter not in valid_time_filters:
            raise ValueError(f"time_filter must be one of: {valid_time_filters}")
        
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch posts from Reddit.

        Args:
            **kwargs: Optional override parameters

        Returns:
            List of SourcedContent objects
        """
        limit = kwargs.get("limit", self.limit)
        sort_by = kwargs.get("sort_by", self.sort_by)
        time_filter = kwargs.get("time_filter", self.time_filter)
        
        contents = []
        
        try:
            subreddit = self.reddit.subreddit(self.subreddit)
            
            # Get posts based on sort method
            if sort_by == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort_by == "new":
                submissions = subreddit.new(limit=limit)
            elif sort_by == "rising":
                submissions = subreddit.rising(limit=limit)
            elif sort_by == "top":
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_by == "controversial":
                submissions = subreddit.controversial(time_filter=time_filter, limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                # Build content text
                content_parts = []
                if submission.selftext:
                    content_parts.append(submission.selftext)
                
                # Add post metadata to content
                content_parts.append(f"\n[Score: {submission.score} | Comments: {submission.num_comments}]")
                
                content = "\n".join(content_parts)
                
                # Build metadata
                metadata = {
                    "subreddit": self.subreddit,
                    "post_id": submission.id,
                    "score": submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    "is_self": submission.is_self,
                    "link_flair_text": submission.link_flair_text,
                    "domain": submission.domain,
                    "permalink": f"https://reddit.com{submission.permalink}",
                    "gilded": submission.gilded,
                    "distinguished": submission.distinguished,
                    "stickied": submission.stickied,
                }
                
                # Convert Unix timestamp to datetime
                published_date = datetime.fromtimestamp(submission.created_utc)
                
                sourced_content = SourcedContent(
                    title=submission.title,
                    content=content,
                    url=submission.url,
                    published_date=published_date,
                    author=str(submission.author) if submission.author else "[deleted]",
                    metadata=metadata,
                )
                
                contents.append(sourced_content)
        
        except Exception as e:
            raise Exception(f"Failed to fetch from Reddit: {str(e)}")
        
        return contents

    def __repr__(self) -> str:
        return f"<RedditSourcer: {self.name} (r/{self.subreddit})>"
