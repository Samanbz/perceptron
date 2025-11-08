"""YouTube sourcer using official YouTube Data API v3."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import os

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

from .base import BaseSourcer, SourcedContent


class YouTubeSourcer(BaseSourcer):
    """
    Sourcer for YouTube videos using official YouTube Data API v3.
    
    YouTube Data API:
    - Free tier: 10,000 units/day
    - Search costs: 100 units per request
    - ~100 searches per day on free tier
    
    Setup:
    1. Go to: https://console.cloud.google.com/
    2. Create a new project (or select existing)
    3. Enable "YouTube Data API v3"
    4. Create credentials → API Key
    5. Copy your API key
    6. Set YOUTUBE_API_KEY environment variable
    """

    def __init__(
        self,
        search_query: Optional[str] = None,
        channel_id: Optional[str] = None,
        api_key: Optional[str] = None,
        name: Optional[str] = None,
        max_results: int = 25,
        order: str = "relevance",  # date, rating, relevance, title, viewCount
        published_after: Optional[datetime] = None,
    ):
        """
        Initialize YouTube sourcer.

        Args:
            search_query: Search keywords
            channel_id: Specific channel ID to search within
            api_key: YouTube API key (or set YOUTUBE_API_KEY env var)
            name: Optional name for this sourcer
            max_results: Maximum videos to fetch (default: 25, max: 50)
            order: Sort order (default: relevance)
            published_after: Only fetch videos after this date
        """
        super().__init__(name)
        
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError(
                "google-api-python-client is not installed. "
                "Install it with: pip install google-api-python-client"
            )
        
        self.search_query = search_query
        self.channel_id = channel_id
        self.max_results = min(max_results, 50)  # API limit
        self.order = order
        self.published_after = published_after
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        
        self.validate_config()
        
        # Initialize YouTube client
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def validate_config(self, **kwargs) -> bool:
        """Validate YouTube sourcer configuration."""
        if not self.api_key:
            raise ValueError(
                "YouTube API key required. Set YOUTUBE_API_KEY environment variable "
                "or pass as parameter. Get key at: https://console.cloud.google.com/"
            )
        
        if not self.search_query and not self.channel_id:
            raise ValueError("Either search_query or channel_id is required")
        
        valid_orders = ["date", "rating", "relevance", "title", "viewCount"]
        if self.order not in valid_orders:
            raise ValueError(f"order must be one of: {valid_orders}")
        
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch videos from YouTube.

        Args:
            **kwargs: Optional override parameters

        Returns:
            List of SourcedContent objects
        """
        max_results = kwargs.get("max_results", self.max_results)
        order = kwargs.get("order", self.order)
        
        contents = []
        
        try:
            # Build search request
            search_params = {
                "part": "snippet",
                "maxResults": max_results,
                "order": order,
                "type": "video",
                "relevanceLanguage": "en",
            }
            
            if self.search_query:
                search_params["q"] = self.search_query
            
            if self.channel_id:
                search_params["channelId"] = self.channel_id
            
            if self.published_after:
                search_params["publishedAfter"] = self.published_after.isoformat() + "Z"
            
            # Execute search
            search_response = self.youtube.search().list(**search_params).execute()
            
            # Get video IDs for detailed statistics
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            if not video_ids:
                return contents
            
            # Get video statistics and details
            videos_response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids)
            ).execute()
            
            for video in videos_response.get("items", []):
                snippet = video["snippet"]
                statistics = video.get("statistics", {})
                content_details = video.get("contentDetails", {})
                
                # Parse publish date
                published_date = None
                if snippet.get("publishedAt"):
                    try:
                        published_date = datetime.fromisoformat(
                            snippet["publishedAt"].replace("Z", "+00:00")
                        )
                    except:
                        pass
                
                # Build content text
                content_parts = [snippet.get("description", "")]
                
                # Add statistics
                stats_text = (
                    f"\n\n[Views: {statistics.get('viewCount', 0):,} | "
                    f"Likes: {statistics.get('likeCount', 0):,} | "
                    f"Comments: {statistics.get('commentCount', 0):,}]"
                )
                content_parts.append(stats_text)
                
                content = "".join(content_parts)
                
                # Build metadata
                metadata = {
                    "platform": "youtube",
                    "video_id": video["id"],
                    "channel_id": snippet["channelId"],
                    "channel_title": snippet["channelTitle"],
                    "view_count": int(statistics.get("viewCount", 0)),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                    "duration": content_details.get("duration", ""),
                    "tags": snippet.get("tags", []),
                    "category_id": snippet.get("categoryId", ""),
                    "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                }
                
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                
                sourced_content = SourcedContent(
                    title=snippet["title"],
                    content=content,
                    url=video_url,
                    published_date=published_date,
                    author=snippet["channelTitle"],
                    metadata=metadata,
                )
                
                contents.append(sourced_content)
        
        except HttpError as e:
            if e.resp.status == 403:
                raise Exception(
                    "YouTube API quota exceeded or invalid API key. "
                    "Check your quotas at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas"
                )
            else:
                raise Exception(f"YouTube API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to fetch from YouTube: {str(e)}")
        
        return contents

    def __repr__(self) -> str:
        if self.channel_id:
            return f"<YouTubeSourcer: {self.name} (Channel: {self.channel_id})>"
        return f"<YouTubeSourcer: {self.name} ({self.search_query})>"
