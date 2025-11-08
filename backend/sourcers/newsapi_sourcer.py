"""NewsAPI sourcer for news articles from various sources."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os

try:
    from newsapi import NewsApiClient
    from newsapi.newsapi_exception import NewsAPIException
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

from .base import BaseSourcer, SourcedContent


class NewsAPISourcer(BaseSourcer):
    """
    Sourcer for news articles using NewsAPI.org.
    
    NewsAPI:
    - Free tier: 100 requests/day, 1 request/second
    - Developer tier: $449/month (unlimited requests)
    - Access to 80,000+ news sources
    
    Setup:
    1. Sign up at: https://newsapi.org/register
    2. Get your API key
    3. Set NEWSAPI_KEY environment variable
    
    Free tier limitations:
    - Only articles from last 30 days
    - No access to full content (only description)
    - Rate limited to 1000 requests/day (developer account)
    """

    def __init__(
        self,
        query: Optional[str] = None,
        sources: Optional[str] = None,  # Comma-separated source IDs
        domains: Optional[str] = None,  # Comma-separated domains
        category: Optional[str] = None,  # business, entertainment, general, health, science, sports, technology
        country: Optional[str] = None,  # 2-letter country code
        api_key: Optional[str] = None,
        name: Optional[str] = None,
        max_articles: int = 100,
        language: str = "en",
        sort_by: str = "publishedAt",  # relevancy, popularity, publishedAt
        from_date: Optional[datetime] = None,
    ):
        """
        Initialize NewsAPI sourcer.

        Args:
            query: Keywords or phrases to search for
            sources: Comma-separated source IDs (e.g., "bbc-news,cnn")
            domains: Comma-separated domains (e.g., "bbc.co.uk,techcrunch.com")
            category: News category
            country: 2-letter country code (e.g., "us")
            api_key: NewsAPI key (or set NEWSAPI_KEY env var)
            name: Optional name for this sourcer
            max_articles: Maximum articles to fetch (default: 100)
            language: Language code (default: en)
            sort_by: Sort order (default: publishedAt)
            from_date: Fetch articles from this date onwards
        """
        super().__init__(name)
        
        if not NEWSAPI_AVAILABLE:
            raise ImportError(
                "newsapi-python is not installed. "
                "Install it with: pip install newsapi-python"
            )
        
        self.query = query
        self.sources = sources
        self.domains = domains
        self.category = category
        self.country = country
        self.max_articles = max_articles
        self.language = language
        self.sort_by = sort_by
        self.from_date = from_date or (datetime.now() - timedelta(days=7))
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        
        self.validate_config()
        
        # Initialize NewsAPI client
        self.newsapi = NewsApiClient(api_key=self.api_key)

    def validate_config(self, **kwargs) -> bool:
        """Validate NewsAPI sourcer configuration."""
        if not self.api_key:
            raise ValueError(
                "NewsAPI key required. Set NEWSAPI_KEY environment variable "
                "or pass as parameter. Get key at: https://newsapi.org/register"
            )
        
        if self.category:
            valid_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
            if self.category not in valid_categories:
                raise ValueError(f"category must be one of: {valid_categories}")
        
        if self.sort_by:
            valid_sorts = ["relevancy", "popularity", "publishedAt"]
            if self.sort_by not in valid_sorts:
                raise ValueError(f"sort_by must be one of: {valid_sorts}")
        
        return True

    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch articles from NewsAPI.

        Args:
            **kwargs: Optional override parameters

        Returns:
            List of SourcedContent objects
        """
        contents = []
        
        try:
            # Determine which endpoint to use
            if self.category or self.country:
                # Use top-headlines endpoint
                response = self.newsapi.get_top_headlines(
                    q=self.query,
                    sources=self.sources,
                    category=self.category,
                    country=self.country,
                    language=self.language,
                    page_size=min(self.max_articles, 100),  # API limit
                )
            else:
                # Use everything endpoint
                from_date_str = self.from_date.strftime("%Y-%m-%d")
                
                response = self.newsapi.get_everything(
                    q=self.query,
                    sources=self.sources,
                    domains=self.domains,
                    from_param=from_date_str,
                    language=self.language,
                    sort_by=self.sort_by,
                    page_size=min(self.max_articles, 100),  # API limit
                )
            
            if response["status"] != "ok":
                raise Exception(f"NewsAPI returned status: {response['status']}")
            
            articles = response.get("articles", [])
            
            for article in articles:
                # Parse publish date
                published_date = None
                if article.get("publishedAt"):
                    try:
                        published_date = datetime.fromisoformat(
                            article["publishedAt"].replace("Z", "+00:00")
                        )
                    except:
                        pass
                
                # Build content (NewsAPI free tier doesn't provide full content)
                content_parts = []
                if article.get("description"):
                    content_parts.append(article["description"])
                
                # Note about full content
                if article.get("content"):
                    # NewsAPI truncates content on free tier
                    content_parts.append(f"\n\n{article['content']}")
                
                content = "\n".join(content_parts) if content_parts else ""
                
                # Build metadata
                metadata = {
                    "platform": "newsapi",
                    "source_id": article.get("source", {}).get("id", ""),
                    "source_name": article.get("source", {}).get("name", ""),
                    "author": article.get("author", ""),
                    "url_to_image": article.get("urlToImage", ""),
                }
                
                sourced_content = SourcedContent(
                    title=article.get("title", "Untitled"),
                    content=content,
                    url=article.get("url", ""),
                    published_date=published_date,
                    author=article.get("author", "Unknown"),
                    metadata=metadata,
                )
                
                contents.append(sourced_content)
        
        except NewsAPIException as e:
            if "rateLimited" in str(e):
                raise Exception(
                    "NewsAPI rate limit exceeded. Free tier: 100 requests/day. "
                    "Check usage at: https://newsapi.org/account"
                )
            elif "apiKeyInvalid" in str(e):
                raise Exception(
                    "Invalid NewsAPI key. Get a valid key at: https://newsapi.org/register"
                )
            else:
                raise Exception(f"NewsAPI error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to fetch from NewsAPI: {str(e)}")
        
        return contents

    def __repr__(self) -> str:
        if self.category:
            return f"<NewsAPISourcer: {self.name} (Category: {self.category})>"
        elif self.sources:
            return f"<NewsAPISourcer: {self.name} (Sources: {self.sources})>"
        return f"<NewsAPISourcer: {self.name} ({self.query})>"
