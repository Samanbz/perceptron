"""RSS feed sourcer implementation."""

import feedparser
from typing import List, Optional
from datetime import datetime
import time

from .base import BaseSourcer, SourcedContent


class RSSSourcer(BaseSourcer):
    """Sourcer for RSS/Atom feeds."""

    def __init__(self, feed_url: str, name: Optional[str] = None, max_entries: int = 50):
        """
        Initialize RSS sourcer.

        Args:
            feed_url: URL of the RSS/Atom feed
            name: Optional name for this sourcer
            max_entries: Maximum number of entries to fetch (default: 50)
        """
        super().__init__(name)
        self.feed_url = feed_url
        self.max_entries = max_entries
        self.validate_config(feed_url=feed_url)

    def validate_config(self, **kwargs) -> bool:
        """
        Validate RSS feed configuration.

        Args:
            feed_url: URL of the RSS feed

        Returns:
            True if valid

        Raises:
            ValueError: If feed_url is missing or invalid
        """
        feed_url = kwargs.get("feed_url", self.feed_url if hasattr(self, "feed_url") else None)
        
        if not feed_url:
            raise ValueError("feed_url is required")
        
        if not isinstance(feed_url, str):
            raise ValueError("feed_url must be a string")
        
        if not feed_url.startswith(("http://", "https://")):
            raise ValueError("feed_url must start with http:// or https://")
        
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch entries from the RSS feed.

        Args:
            **kwargs: Optional override parameters (feed_url, max_entries)

        Returns:
            List of SourcedContent objects

        Raises:
            Exception: If feed parsing fails
        """
        feed_url = kwargs.get("feed_url", self.feed_url)
        max_entries = kwargs.get("max_entries", self.max_entries)

        # Parse the feed
        feed = feedparser.parse(feed_url)
        
        if feed.bozo and not feed.entries:
            # bozo flag indicates malformed XML, but sometimes feeds work anyway
            raise Exception(f"Failed to parse feed: {feed.get('bozo_exception', 'Unknown error')}")
        
        contents = []
        
        for entry in feed.entries[:max_entries]:
            # Extract publication date
            published_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6])
            
            # Extract content (try different fields)
            content = ""
            if hasattr(entry, "content"):
                content = entry.content[0].value if entry.content else ""
            elif hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description
            
            # Extract author
            author = None
            if hasattr(entry, "author"):
                author = entry.author
            elif hasattr(entry, "authors") and entry.authors:
                author = entry.authors[0].get("name", "")
            
            # Build metadata
            metadata = {
                "feed_title": feed.feed.get("title", ""),
                "feed_url": feed_url,
                "entry_id": entry.get("id", ""),
                "tags": [tag.term for tag in entry.get("tags", [])] if hasattr(entry, "tags") else [],
            }
            
            sourced_content = SourcedContent(
                title=entry.get("title", "Untitled"),
                content=content,
                url=entry.get("link", None),
                published_date=published_date,
                author=author,
                metadata=metadata,
            )
            
            contents.append(sourced_content)
        
        return contents

    def __repr__(self) -> str:
        return f"<RSSSourcer: {self.name} ({self.feed_url})>"
