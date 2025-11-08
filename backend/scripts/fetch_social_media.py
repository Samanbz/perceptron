"""
Comprehensive social media data fetcher for Perceptron.

This script fetches data from all configured social media platforms
and stores it in the database for keyword extraction and analysis.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from sourcers import RedditSourcer, TwitterSourcer
    from storage import ArticleRepository
    SOURCERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    SOURCERS_AVAILABLE = False


class SocialMediaConfig:
    """Configuration for social media data collection."""
    
    # Reddit sources
    REDDIT_SOURCES = [
        {
            "name": "Tech News",
            "subreddit": "technology",
            "limit": 100,
            "sort_by": "hot",
            "enabled": True,
        },
        {
            "name": "AI & ML Research",
            "subreddit": "MachineLearning",
            "limit": 50,
            "sort_by": "top",
            "time_filter": "week",
            "enabled": True,
        },
        {
            "name": "World News",
            "subreddit": "worldnews",
            "limit": 100,
            "sort_by": "hot",
            "enabled": True,
        },
        {
            "name": "Business & Finance",
            "subreddit": "business",
            "limit": 50,
            "sort_by": "top",
            "time_filter": "day",
            "enabled": True,
        },
        {
            "name": "Cybersecurity",
            "subreddit": "cybersecurity",
            "limit": 50,
            "sort_by": "hot",
            "enabled": True,
        },
        {
            "name": "Startup Discussions",
            "subreddit": "startups",
            "limit": 30,
            "sort_by": "top",
            "time_filter": "week",
            "enabled": True,
        },
        {
            "name": "Data Science",
            "subreddit": "datascience",
            "limit": 30,
            "sort_by": "hot",
            "enabled": True,
        },
        {
            "name": "Science News",
            "subreddit": "science",
            "limit": 50,
            "sort_by": "hot",
            "enabled": True,
        },
    ]
    
    # Twitter sources
    TWITTER_SOURCES = [
        {
            "name": "AI Regulation",
            "search_query": "artificial intelligence regulation OR AI policy OR AI governance",
            "mode": "term",
            "max_tweets": 100,
            "enabled": True,
        },
        {
            "name": "Venture Capital",
            "search_query": "venture capital OR startup funding OR Series A OR Series B",
            "mode": "term",
            "max_tweets": 50,
            "enabled": True,
        },
        {
            "name": "Cybersecurity Threats",
            "search_query": "cybersecurity OR data breach OR ransomware OR cyber attack",
            "mode": "term",
            "max_tweets": 50,
            "enabled": True,
        },
        {
            "name": "Tech Acquisitions",
            "search_query": "tech acquisition OR merger OR M&A technology",
            "mode": "term",
            "max_tweets": 30,
            "enabled": True,
        },
        {
            "name": "Climate Tech",
            "search_query": "climate tech OR green technology OR sustainability",
            "mode": "term",
            "max_tweets": 30,
            "enabled": True,
        },
        {
            "name": "Blockchain & Web3",
            "search_query": "blockchain OR web3 OR cryptocurrency regulation",
            "mode": "term",
            "max_tweets": 30,
            "enabled": True,
        },
    ]


class SocialMediaFetcher:
    """Handles fetching and storing social media data."""
    
    def __init__(self):
        self.stats = {
            "total_fetched": 0,
            "total_stored": 0,
            "errors": [],
            "sources_processed": 0,
            "start_time": datetime.now(),
        }
        self.check_credentials()
    
    def check_credentials(self):
        """Check if required credentials are available."""
        self.reddit_available = bool(
            os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")
        )
        
        if not self.reddit_available:
            print("\n⚠️  Reddit credentials not found!")
            print("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables")
            print("Get credentials at: https://www.reddit.com/prefs/apps\n")
    
    async def fetch_reddit(self, config: Dict[str, Any]) -> List[Any]:
        """Fetch posts from Reddit."""
        if not self.reddit_available:
            return []
        
        try:
            sourcer = RedditSourcer(
                subreddit=config["subreddit"],
                name=config["name"],
                limit=config["limit"],
                sort_by=config["sort_by"],
                time_filter=config.get("time_filter", "day"),
            )
            
            print(f"  📥 Fetching from r/{config['subreddit']}...", end=" ")
            contents = await sourcer.fetch()
            print(f"✓ {len(contents)} posts")
            
            return contents
            
        except Exception as e:
            error_msg = f"Reddit r/{config['subreddit']}: {str(e)}"
            self.stats["errors"].append(error_msg)
            print(f"✗ Error: {e}")
            return []
    
    async def fetch_twitter(self, config: Dict[str, Any]) -> List[Any]:
        """Fetch tweets from Twitter."""
        try:
            sourcer = TwitterSourcer(
                search_query=config.get("search_query"),
                username=config.get("username"),
                hashtag=config.get("hashtag"),
                mode=config["mode"],
                max_tweets=config["max_tweets"],
                name=config["name"],
            )
            
            query_display = (
                config.get("search_query") or 
                f"@{config.get('username')}" or 
                f"#{config.get('hashtag')}"
            )
            print(f"  🐦 Fetching tweets: {query_display[:50]}...", end=" ")
            
            contents = await sourcer.fetch()
            print(f"✓ {len(contents)} tweets")
            
            return contents
            
        except Exception as e:
            error_msg = f"Twitter {config['name']}: {str(e)}"
            self.stats["errors"].append(error_msg)
            print(f"✗ Error: {e}")
            return []
    
    async def store_content(self, contents: List[Any], source_type: str, source_name: str):
        """Store content in the database."""
        if not contents:
            return
        
        try:
            repo = ArticleRepository()
            stored = 0
            
            for content in contents:
                try:
                    # Store article with metadata
                    # Note: Adjust this based on your actual ArticleRepository implementation
                    await repo.store_article(
                        title=content.title,
                        content=content.content,
                        url=content.url,
                        source=f"{source_type}:{source_name}",
                        author=content.author,
                        published_date=content.published_date,
                        metadata={
                            **content.metadata,
                            "platform": source_type,
                            "source_name": source_name,
                        }
                    )
                    stored += 1
                except Exception as e:
                    # Skip individual items that fail
                    continue
            
            self.stats["total_stored"] += stored
            print(f"  💾 Stored {stored}/{len(contents)} items")
            
        except Exception as e:
            error_msg = f"Storage for {source_name}: {str(e)}"
            self.stats["errors"].append(error_msg)
            print(f"  ✗ Storage error: {e}")
    
    async def fetch_all_reddit(self):
        """Fetch from all configured Reddit sources."""
        print("\n" + "=" * 70)
        print("📱 FETCHING REDDIT DATA")
        print("=" * 70)
        
        if not self.reddit_available:
            print("⊘ Skipped (credentials not configured)")
            return
        
        for config in SocialMediaConfig.REDDIT_SOURCES:
            if not config.get("enabled", True):
                print(f"  ⊘ Skipped: r/{config['subreddit']} (disabled)")
                continue
            
            self.stats["sources_processed"] += 1
            contents = await self.fetch_reddit(config)
            self.stats["total_fetched"] += len(contents)
            
            # Store in database
            if contents:
                await self.store_content(contents, "reddit", f"r/{config['subreddit']}")
            
            # Small delay to respect rate limits
            await asyncio.sleep(2)
    
    async def fetch_all_twitter(self):
        """Fetch from all configured Twitter sources."""
        print("\n" + "=" * 70)
        print("🐦 FETCHING TWITTER DATA")
        print("=" * 70)
        
        for config in SocialMediaConfig.TWITTER_SOURCES:
            if not config.get("enabled", True):
                print(f"  ⊘ Skipped: {config['name']} (disabled)")
                continue
            
            self.stats["sources_processed"] += 1
            contents = await self.fetch_twitter(config)
            self.stats["total_fetched"] += len(contents)
            
            # Store in database
            if contents:
                query = (
                    config.get("search_query") or 
                    config.get("username") or 
                    config.get("hashtag")
                )
                await self.store_content(contents, "twitter", config["name"])
            
            # Delay to respect rate limits and Nitter instances
            await asyncio.sleep(5)
    
    def print_summary(self):
        """Print collection summary."""
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        print("\n" + "=" * 70)
        print("📊 COLLECTION SUMMARY")
        print("=" * 70)
        
        print(f"\n⏱️  Duration: {duration:.1f} seconds")
        print(f"📋 Sources processed: {self.stats['sources_processed']}")
        print(f"📥 Total items fetched: {self.stats['total_fetched']}")
        print(f"💾 Total items stored: {self.stats['total_stored']}")
        
        if self.stats["errors"]:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"][:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(self.stats["errors"]) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more")
        else:
            print("\n✅ No errors!")
        
        print("\n" + "=" * 70)


async def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print("🚀 PERCEPTRON SOCIAL MEDIA DATA COLLECTOR")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not SOURCERS_AVAILABLE:
        print("\n❌ Required modules not available!")
        print("Make sure you've installed: pip install praw ntscraper")
        return
    
    fetcher = SocialMediaFetcher()
    
    # Fetch from all sources
    await fetcher.fetch_all_reddit()
    await fetcher.fetch_all_twitter()
    
    # Print summary
    fetcher.print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return stats for programmatic use
    return fetcher.stats


if __name__ == "__main__":
    try:
        stats = asyncio.run(main())
        
        # Exit with error code if there were issues
        if stats and stats["errors"]:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
