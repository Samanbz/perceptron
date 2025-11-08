"""
Background scheduler for fetching content from all configured sources
Handles RSS feeds, blog scraping, and web scraping
"""
import asyncio
import sys

# Fix for Playwright on Windows - must be set before any async operations
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import time
from datetime import datetime, timedelta
from typing import List
import logging

from sourcers import RSSSourcer
from sourcers.web_scraper import BlogScraper, GenericWebScraper
from sourcers.playwright_scraper import PlaywrightScraper
from storage import (
    ContentRepository,
    SourceConfigRepository,
    SourceConfigModel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SourceScheduler:
    """Scheduler that automatically fetches content from configured sources"""
    
    def __init__(self, check_interval_seconds: int = 60):
        """
        Initialize scheduler
        
        Args:
            check_interval_seconds: How often to check for sources that need fetching
        """
        self.check_interval = check_interval_seconds
        self.running = False
        self.config_repo = SourceConfigRepository()
        self.content_repo = ContentRepository()
        self.playwright_scraper = None  # Lazy initialization
        self.stats = {
            "cycles_completed": 0,
            "total_sources_fetched": 0,
            "total_items_saved": 0,
            "errors": 0,
            "last_cycle_time": None
        }
    
    def should_fetch(self, source: SourceConfigModel) -> bool:
        """Check if a source should be fetched now"""
        if not source.enabled:
            return False
        
        if source.next_fetch_at is None:
            return True  # Never fetched before
        
        return datetime.utcnow() >= source.next_fetch_at
    
    async def fetch_rss_source(self, source: SourceConfigModel) -> dict:
        """Fetch content from an RSS source"""
        try:
            logger.info(f"Fetching RSS: {source.source_name}")
            
            max_entries = source.config.get('max_entries', 50)
            sourcer = RSSSourcer(
                feed_url=source.source_url,
                name=source.source_name,
                max_entries=max_entries
            )
            
            contents = await sourcer.fetch()
            
            if contents:
                stats = self.content_repo.save_batch(
                    contents,
                    source_type=source.source_type,
                    source_name=source.source_name,
                    source_url=source.source_url
                )
                
                # Update source stats
                self.config_repo.update_fetch_status(
                    source.id,
                    items_count=stats['saved']
                )
                
                logger.info(f"✅ RSS {source.source_name}: {stats['saved']} new items, {stats['duplicates']} duplicates")
                return stats
            else:
                logger.warning(f"⚠️ RSS {source.source_name}: No content fetched")
                self.config_repo.update_fetch_status(source.id, items_fetched=0)
                return {"saved": 0, "duplicates": 0}
                
        except Exception as e:
            logger.error(f"❌ RSS {source.source_name}: {str(e)}")
            self.config_repo.update_fetch_status(source.id, items_fetched=0, error=str(e))
            return {"error": str(e)}
    
    async def fetch_blog_source(self, source: SourceConfigModel) -> dict:
        """Fetch content from a blog source"""
        try:
            logger.info(f"Scraping blog: {source.source_name}")
            
            selectors = source.config.get('selectors', {}) if source.config else {}
            use_playwright = source.config.get('use_playwright', False) if source.config else False
            
            # Use Playwright for sources that need it (bot protection, JavaScript, etc.)
            if use_playwright:
                logger.info(f"🎭 Using Playwright for {source.source_name}")
                return await self.fetch_with_playwright(source)
            
            # Otherwise use regular scraping
            max_pages = source.config.get('max_pages', 5) if source.config else 5
            
            scraper = GenericWebScraper({
                'base_url': source.source_url,
                'name': source.source_name,
                'max_pages': max_pages,
                'selectors': selectors
            })
            
            contents = await scraper.scrape()
            
            if contents:
                stats = self.content_repo.save_batch(
                    contents,
                    source_type=source.source_type,
                    source_name=source.source_name,
                    source_url=source.source_url
                )
                
                self.config_repo.update_fetch_status(
                    source.id,
                    items_fetched=stats['saved']
                )
                
                logger.info(f"✅ Blog {source.source_name}: {stats['saved']} new items, {stats['duplicates']} duplicates")
                return stats
            else:
                logger.warning(f"⚠️ Blog {source.source_name}: No content scraped")
                self.config_repo.update_fetch_status(source.id, items_fetched=0)
                return {"saved": 0, "duplicates": 0}
                
        except Exception as e:
            logger.error(f"❌ Blog {source.source_name}: {str(e)}")
            self.config_repo.update_fetch_status(source.id, items_fetched=0, error=str(e))
            return {"error": str(e)}
    
    async def fetch_with_playwright(self, source: SourceConfigModel) -> dict:
        """Fetch content using Playwright for bot-protected or JavaScript-heavy sites"""
        try:
            # Initialize Playwright scraper if not already done
            if self.playwright_scraper is None:
                self.playwright_scraper = PlaywrightScraper(timeout=60000)
                await self.playwright_scraper.start()
            
            selectors = source.config.get('selectors', {})
            max_items = source.config.get('max_items', 10)
            
            articles = await self.playwright_scraper.scrape_blog(
                url=source.source_url,
                selectors=selectors,
                max_items=max_items
            )
            
            if articles:
                stats = self.content_repo.save_batch(
                    articles,
                    source_type=source.source_type,
                    source_name=source.source_name,
                    source_url=source.source_url
                )
                
                self.config_repo.update_fetch_status(
                    source.id,
                    items_fetched=stats['saved']
                )
                
                logger.info(f"✅ Playwright {source.source_name}: {stats['saved']} new items, {stats['duplicates']} duplicates")
                return stats
            else:
                logger.warning(f"⚠️ Playwright {source.source_name}: No content scraped")
                self.config_repo.update_fetch_status(source.id, items_fetched=0)
                return {"saved": 0, "duplicates": 0}
                
        except Exception as e:
            logger.error(f"❌ Playwright {source.source_name}: {str(e)}")
            self.config_repo.update_fetch_status(source.id, items_fetched=0, error=str(e))
            return {"error": str(e)}
    
    async def fetch_web_source(self, source: SourceConfigModel) -> dict:
        """Fetch content from a generic web source"""
        try:
            logger.info(f"Scraping web: {source.source_name}")
            
            selectors = source.config.get('selectors', {})
            max_pages = source.config.get('max_pages', 10)
            
            scraper = GenericWebScraper({
                'base_url': source.source_url,
                'name': source.source_name,
                'max_pages': max_pages,
                'selectors': selectors
            })
            
            contents = await scraper.scrape()
            
            if contents:
                stats = self.content_repo.save_batch(
                    contents,
                    source_type=source.source_type,
                    source_name=source.source_name,
                    source_url=source.source_url
                )
                
                self.config_repo.update_fetch_status(
                    source.id,
                    items_fetched=stats['saved']
                )
                
                logger.info(f"✅ Web {source.source_name}: {stats['saved']} new items")
                return stats
            else:
                logger.warning(f"⚠️ Web {source.source_name}: No content scraped")
                self.config_repo.update_fetch_status(source.id, items_fetched=0)
                return {"saved": 0, "duplicates": 0}
                
        except Exception as e:
            logger.error(f"❌ Web {source.source_name}: {str(e)}")
            self.config_repo.update_fetch_status(source.id, items_fetched=0, error=str(e))
            return {"error": str(e)}
    
    async def fetch_source(self, source: SourceConfigModel) -> dict:
        """Fetch content from any type of source"""
        if source.source_type == "rss":
            return await self.fetch_rss_source(source)
        elif source.source_type == "blog_scrape":
            return await self.fetch_blog_source(source)
        elif source.source_type == "web_scrape":
            return await self.fetch_web_source(source)
        else:
            logger.error(f"Unknown source type: {source.source_type}")
            return {"error": f"Unknown source type: {source.source_type}"}
    
    async def run_cycle(self):
        """Run one fetch cycle - check all sources and fetch those that are due"""
        logger.info("Starting fetch cycle...")
        
        # Refresh session to get latest data from database
        self.config_repo.session.expire_all()
        
        # Get all sources
        sources = self.config_repo.list_sources(enabled_only=True)
        
        if not sources:
            logger.info("No enabled sources configured")
            return
        
        # Check which sources need fetching
        sources_to_fetch = [s for s in sources if self.should_fetch(s)]
        
        if not sources_to_fetch:
            logger.info(f"No sources due for fetching (checked {len(sources)} sources)")
            return
        
        logger.info(f"Fetching {len(sources_to_fetch)} sources...")
        
        # Fetch from each source
        results = []
        for source in sources_to_fetch:
            result = await self.fetch_source(source)
            results.append({
                "source": source.source_name,
                "type": source.source_type,
                "result": result
            })
        
        # Summary
        successful = sum(1 for r in results if "error" not in r["result"])
        failed = sum(1 for r in results if "error" in r["result"])
        total_saved = sum(r["result"].get("saved", 0) for r in results)
        
        # Update stats
        self.stats["cycles_completed"] += 1
        self.stats["total_sources_fetched"] += len(sources_to_fetch)
        self.stats["total_items_saved"] += total_saved
        self.stats["errors"] += failed
        self.stats["last_cycle_time"] = datetime.utcnow().isoformat()
        
        logger.info(f"Cycle complete: {successful} successful, {failed} failed, {total_saved} new items saved")
    
    async def run(self):
        """Run the scheduler continuously"""
        self.running = True
        logger.info(f"Scheduler started (checking every {self.check_interval} seconds)")
        
        while self.running:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Error in scheduler cycle: {e}")
            
            # Wait before next cycle
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False
        
        # Close Playwright if it was initialized
        if self.playwright_scraper:
            asyncio.create_task(self.playwright_scraper.close())
        
        self.config_repo.close()
        self.content_repo.close()
    
    def is_running(self) -> bool:
        """Check if scheduler is currently running"""
        return self.running
    
    def get_stats(self) -> dict:
        """Get scheduler statistics"""
        return self.stats.copy()


# Singleton instance
_scheduler_instance = None


def get_scheduler() -> SourceScheduler:
    """Get or create scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SourceScheduler(check_interval_seconds=60)
    return _scheduler_instance


async def start_scheduler():
    """Start the background scheduler"""
    scheduler = get_scheduler()
    await scheduler.run()


if __name__ == "__main__":
    # Run scheduler standalone
    asyncio.run(start_scheduler())
