"""Twitter/X sourcer using ntscraper (no API key required)."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

try:
    from ntscraper import Nitter
    NTSCRAPER_AVAILABLE = True
except ImportError:
    NTSCRAPER_AVAILABLE = False

from .base import BaseSourcer, SourcedContent


class TwitterSourcer(BaseSourcer):
    """
    Sourcer for Twitter/X posts using Nitter instances (no API key needed).
    
    Uses ntscraper library which scrapes through public Nitter instances.
    No authentication or API keys required, but may be slower and less reliable
    than official API.
    
    Limitations:
    - Depends on public Nitter instances availability
    - May have rate limits from Nitter instances
    - Cannot access private accounts
    - Limited historical data
    
    For production use with high volume, consider Twitter API v2 with academic access.
    """

    def __init__(
        self,
        search_query: Optional[str] = None,
        username: Optional[str] = None,
        hashtag: Optional[str] = None,
        name: Optional[str] = None,
        max_tweets: int = 50,
        mode: str = "term",  # term, hashtag, user
    ):
        """
        Initialize Twitter sourcer.

        Args:
            search_query: Search query/keywords (for mode='term')
            username: Twitter username without @ (for mode='user')
            hashtag: Hashtag without # (for mode='hashtag')
            name: Optional name for this sourcer
            max_tweets: Maximum number of tweets to fetch (default: 50)
            mode: Search mode - 'term', 'hashtag', or 'user' (default: term)
        """
        super().__init__(name)
        
        if not NTSCRAPER_AVAILABLE:
            raise ImportError(
                "ntscraper is not installed. Install it with: pip install ntscraper"
            )
        
        self.search_query = search_query
        self.username = username
        self.hashtag = hashtag
        self.max_tweets = max_tweets
        self.mode = mode
        
        self.validate_config()
        
        # Initialize Nitter scraper
        self.scraper = Nitter(log_level=1, skip_instance_check=False)

    def validate_config(self, **kwargs) -> bool:
        """Validate Twitter sourcer configuration."""
        mode = kwargs.get("mode", self.mode)
        
        if mode not in ["term", "hashtag", "user"]:
            raise ValueError("mode must be one of: term, hashtag, user")
        
        if mode == "term" and not self.search_query:
            raise ValueError("search_query is required for mode='term'")
        
        if mode == "user" and not self.username:
            raise ValueError("username is required for mode='user'")
        
        if mode == "hashtag" and not self.hashtag:
            raise ValueError("hashtag is required for mode='hashtag'")
        
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch tweets from Twitter/X.

        Args:
            **kwargs: Optional override parameters

        Returns:
            List of SourcedContent objects
        """
        max_tweets = kwargs.get("max_tweets", self.max_tweets)
        mode = kwargs.get("mode", self.mode)
        
        contents = []
        
        try:
            tweets_data = None
            
            if mode == "term":
                query = kwargs.get("search_query", self.search_query)
                tweets_data = self.scraper.get_tweets(query, mode="term", number=max_tweets)
            
            elif mode == "user":
                username = kwargs.get("username", self.username)
                tweets_data = self.scraper.get_tweets(username, mode="user", number=max_tweets)
            
            elif mode == "hashtag":
                hashtag = kwargs.get("hashtag", self.hashtag)
                # Remove # if present
                hashtag = hashtag.lstrip("#")
                tweets_data = self.scraper.get_tweets(hashtag, mode="hashtag", number=max_tweets)
            
            if not tweets_data or "tweets" not in tweets_data:
                return contents
            
            for tweet in tweets_data["tweets"]:
                # Extract tweet data
                text = tweet.get("text", "")
                link = tweet.get("link", "")
                date_str = tweet.get("date", "")
                user = tweet.get("user", {})
                stats = tweet.get("stats", {})
                
                # Parse date
                published_date = None
                if date_str:
                    try:
                        # Nitter returns dates in various formats, try to parse
                        published_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except:
                        pass
                
                # Build metadata
                metadata = {
                    "platform": "twitter",
                    "tweet_link": link,
                    "username": user.get("name", ""),
                    "user_profile": user.get("profile_link", ""),
                    "likes": stats.get("likes", 0),
                    "retweets": stats.get("retweets", 0),
                    "quotes": stats.get("quotes", 0),
                    "replies": stats.get("replies", 0),
                    "comments": stats.get("comments", 0),
                    "is_retweet": tweet.get("is-retweet", False),
                    "is_pinned": tweet.get("is-pinned", False),
                    "hashtags": tweet.get("hashtags", []),
                }
                
                # Add media info if present
                if "pictures" in tweet and tweet["pictures"]:
                    metadata["has_media"] = True
                    metadata["media_urls"] = tweet["pictures"]
                
                if "videos" in tweet and tweet["videos"]:
                    metadata["has_video"] = True
                    metadata["video_count"] = tweet["videos"]
                
                sourced_content = SourcedContent(
                    title=f"Tweet by @{user.get('name', 'unknown')}",
                    content=text,
                    url=link,
                    published_date=published_date,
                    author=user.get("name", "unknown"),
                    metadata=metadata,
                )
                
                contents.append(sourced_content)
        
        except Exception as e:
            raise Exception(f"Failed to fetch from Twitter: {str(e)}")
        
        return contents

    def __repr__(self) -> str:
        if self.mode == "user":
            return f"<TwitterSourcer: {self.name} (@{self.username})>"
        elif self.mode == "hashtag":
            return f"<TwitterSourcer: {self.name} (#{self.hashtag})>"
        else:
            return f"<TwitterSourcer: {self.name} ({self.search_query})>"
