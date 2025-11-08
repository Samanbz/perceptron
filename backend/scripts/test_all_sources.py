#!/usr/bin/env python3
"""
Test all sources from config.json to identify which ones work.
"""

import sys
import json
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sourcers.rss_sourcer import RSSSourcer
from sourcers.playwright_scraper import PlaywrightScraper
from sourcers.newsapi_sourcer import NewsAPISourcer
from sourcers.reddit_sourcer import RedditSourcer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


def test_source(source_config: dict, team_name: str) -> dict:
    """
    Test a single source.
    
    Returns dict with: success, message, items_fetched
    """
    source_type = source_config["source_type"]
    source_name = source_config["source_name"]
    source_url = source_config["source_url"]
    config = source_config.get("config", {})
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {source_name} ({source_type})")
    logger.info(f"Team: {team_name}")
    logger.info(f"URL: {source_url}")
    logger.info(f"{'='*80}")
    
    try:
        # Create appropriate sourcer
        if source_type == "rss":
            max_entries = config.get("max_entries", 50)
            sourcer = RSSSourcer(feed_url=source_url, max_entries=max_entries)
            items = []
            import asyncio
            items = asyncio.run(sourcer.fetch())
        elif source_type == "playwright":
            sourcer = PlaywrightScraper(url=source_url, **config)
            import asyncio
            items = asyncio.run(sourcer.scrape())
        elif source_type == "newsapi":
            import os
            api_key = os.getenv("NEWSAPI_KEY")
            if not api_key:
                raise ValueError("NewsAPI key required. Set NEWSAPI_KEY environment variable")
            sourcer = NewsAPISourcer(api_key=api_key)
            query = config.get("query", "")
            domains = config.get("domains", "")
            max_articles = config.get("max_articles", 50)
            import asyncio
            items = asyncio.run(sourcer.fetch(query=query, domains=domains, max_results=max_articles))
        elif source_type == "reddit":
            subreddit = config.get("subreddit", "")
            if not subreddit:
                raise ValueError(f"Subreddit not specified in config for {source_name}")
            sourcer = RedditSourcer(subreddit=subreddit)
            import asyncio
            limit = config.get("limit", 20)
            time_filter = config.get("time_filter", "week")
            sort_by = config.get("sort_by", "hot")
            items = asyncio.run(sourcer.fetch(limit=limit, time_filter=time_filter, sort_by=sort_by))
        else:
            return {
                "success": False,
                "message": f"Unknown source type: {source_type}",
                "items_fetched": 0
            }
        
        # Check if we got any items
        if not items:
            logger.warning(f"⚠️  No items fetched from {source_name}")
            return {
                "success": False,
                "message": "No items returned",
                "items_fetched": 0
            }
        
        # Success
        logger.info(f"✅ Successfully fetched {len(items)} items")
        
        # Show first item as sample
        if items:
            first_item = items[0]
            logger.info(f"\nSample item:")
            logger.info(f"  Title: {first_item.title[:100]}...")
            logger.info(f"  URL: {first_item.url}")
            logger.info(f"  Published: {first_item.published_date}")
            logger.info(f"  Content length: {len(first_item.content or '')} chars")
        
        return {
            "success": True,
            "message": f"Fetched {len(items)} items",
            "items_fetched": len(items)
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "items_fetched": 0
        }


def main():
    """Test all sources from config."""
    config = load_config()
    
    results = []
    total_sources = 0
    successful_sources = 0
    
    # Test each team's sources
    for team in config["teams"]:
        if not team.get("is_active", True):
            logger.info(f"\nSkipping inactive team: {team['team_name']}")
            continue
        
        team_name = team["team_name"]
        logger.info(f"\n\n{'#'*80}")
        logger.info(f"# TESTING TEAM: {team_name}")
        logger.info(f"{'#'*80}")
        
        for source in team["sources"]:
            total_sources += 1
            result = test_source(source, team_name)
            
            results.append({
                "team": team_name,
                "source_name": source["source_name"],
                "source_type": source["source_type"],
                **result
            })
            
            if result["success"]:
                successful_sources += 1
    
    # Print summary
    logger.info(f"\n\n{'='*80}")
    logger.info("SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Total sources tested: {total_sources}")
    logger.info(f"Successful: {successful_sources}")
    logger.info(f"Failed: {total_sources - successful_sources}")
    logger.info(f"Success rate: {successful_sources/total_sources*100:.1f}%")
    
    # List failed sources
    failed = [r for r in results if not r["success"]]
    if failed:
        logger.info(f"\n{'='*80}")
        logger.info("FAILED SOURCES")
        logger.info(f"{'='*80}")
        for r in failed:
            logger.info(f"\n❌ {r['source_name']} ({r['team']})")
            logger.info(f"   Type: {r['source_type']}")
            logger.info(f"   Error: {r['message']}")
    
    # List successful sources
    successful = [r for r in results if r["success"]]
    if successful:
        logger.info(f"\n{'='*80}")
        logger.info("SUCCESSFUL SOURCES")
        logger.info(f"{'='*80}")
        for r in successful:
            logger.info(f"✅ {r['source_name']} ({r['team']}) - {r['items_fetched']} items")
    
    return 0 if successful_sources == total_sources else 1


if __name__ == "__main__":
    sys.exit(main())
