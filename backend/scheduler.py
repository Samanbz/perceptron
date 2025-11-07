"""
Scheduler for periodic content fetching from configured sources.

This module handles:
- Automatic fetching from configured sources
- Deduplication before storage
- Error handling and retry logic
- Statistics tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from storage import (
    ContentRepository,
    SourceConfigRepository,
    SourceConfigModel,
    get_session,
)
from sourcers import RSSSourcer
from sourcers.base import SourcedContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceScheduler:
    """
    Scheduler for periodic content fetching.
    
    Monitors configured sources and fetches new content on schedule.
    """

    def __init__(self, check_interval_seconds: int = 60):
        """
        Initialize scheduler.
        
        Args:
            check_interval_seconds: How often to check for sources to fetch
        """
        self.check_interval = check_interval_seconds
        self.running = False
        self.content_repo = None
        self.config_repo = None

    async def start(self):
        """Start the scheduler."""
        logger.info("Starting source scheduler...")
        self.running = True
        
        # Create repositories
        session = get_session()
        self.content_repo = ContentRepository(session)
        self.config_repo = SourceConfigRepository(session)
        
        try:
            while self.running:
                await self._fetch_cycle()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        finally:
            self.stop()

    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping source scheduler...")
        self.running = False
        
        if self.content_repo:
            self.content_repo.close()
        if self.config_repo:
            self.config_repo.close()

    async def _fetch_cycle(self):
        """Execute one fetch cycle."""
        # Get sources that need fetching
        sources = self.config_repo.get_sources_to_fetch()
        
        if not sources:
            logger.debug("No sources to fetch")
            return
        
        logger.info(f"Found {len(sources)} sources to fetch")
        
        # Fetch from each source
        for source in sources:
            try:
                await self._fetch_source(source)
            except Exception as e:
                logger.error(f"Error fetching from {source.source_name}: {e}")
                self.config_repo.update_fetch_status(
                    source.id,
                    items_fetched=0,
                    error=str(e),
                )

    async def _fetch_source(self, source: SourceConfigModel):
        """
        Fetch content from a single source.
        
        Args:
            source: Source configuration
        """
        logger.info(f"Fetching from {source.source_name} ({source.source_type})")
        
        # Create appropriate sourcer based on type
        sourcer = self._create_sourcer(source)
        
        if not sourcer:
            logger.warning(f"Unknown source type: {source.source_type}")
            return
        
        # Fetch content
        contents = await sourcer.fetch()
        logger.info(f"Fetched {len(contents)} items from {source.source_name}")
        
        # Save to database with deduplication
        stats = self.content_repo.save_batch(
            contents,
            source_type=source.source_type,
            source_name=source.source_name,
            source_url=source.source_url,
        )
        
        logger.info(
            f"Saved {stats['saved']} new items, "
            f"skipped {stats['duplicates']} duplicates from {source.source_name}"
        )
        
        # Update fetch status
        self.config_repo.update_fetch_status(
            source.id,
            items_fetched=stats['saved'],
        )

    def _create_sourcer(self, source: SourceConfigModel):
        """
        Create a sourcer instance based on source configuration.
        
        Args:
            source: Source configuration
        
        Returns:
            Sourcer instance or None
        """
        config = source.config or {}
        
        if source.source_type == 'rss':
            return RSSSourcer(
                feed_url=source.source_url,
                name=source.source_name,
                max_entries=config.get('max_entries', 50),
            )
        
        # Add other source types here as they're implemented
        # elif source.source_type == 'web':
        #     return WebScraperSourcer(...)
        # elif source.source_type == 'api':
        #     return APISourcer(...)
        
        return None


async def run_scheduler():
    """Run the scheduler (main entry point)."""
    scheduler = SourceScheduler(check_interval_seconds=60)
    await scheduler.start()


if __name__ == "__main__":
    asyncio.run(run_scheduler())
