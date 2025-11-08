"""Data source modules for the pipeline."""

from .base import BaseSourcer, SourcedContent
from .rss_sourcer import RSSSourcer
from .reddit_sourcer import RedditSourcer
from .twitter_sourcer import TwitterSourcer
from .linkedin_sourcer import LinkedInSourcer, ProxycurlLinkedInSourcer
from .youtube_sourcer import YouTubeSourcer
from .newsapi_sourcer import NewsAPISourcer

__all__ = [
    "BaseSourcer",
    "SourcedContent",
    "RSSSourcer",
    "RedditSourcer",
    "TwitterSourcer",
    "LinkedInSourcer",
    "ProxycurlLinkedInSourcer",
    "YouTubeSourcer",
    "NewsAPISourcer",
]
