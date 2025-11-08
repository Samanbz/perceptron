"""
Perpetual Data Sourcing Service

Continuously fetches data from all configured RSS feeds.
- Runs every hour
- Maintains 7-day rolling window
- Auto-fetches historical data for new sources
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import os
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.repository import ContentRepository
from sourcers import (
    RSSSourcer,
    RedditSourcer,
    TwitterSourcer,
    YouTubeSourcer,
    NewsAPISourcer,
)
from teams.repository import TeamRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSourcingService:
    """Perpetual data sourcing service."""
    
    def __init__(self):
        self.content_repo = ContentRepository()
        self.team_repo = TeamRepository()
        self.fetch_interval_seconds = 3600  # 1 hour
        self.days_to_keep = 7
        
    def get_all_sources(self) -> List[Dict]:
        """Get all unique sources across all teams."""
        teams = self.team_repo.get_all_teams()
        sources = {}
        
        for team in teams:
            for source in team.sources:
                if source.is_enabled:
                    key = (source.source_name, source.source_url)
                    if key not in sources:
                        # Parse source_config JSON string to dict
                        config = json.loads(source.source_config) if isinstance(source.source_config, str) else (source.source_config or {})
                        
                        sources[key] = {
                            'name': source.source_name,
                            'url': source.source_url,
                            'type': source.source_type,
                            'config': config,  # Include config for sourcer initialization
                        }
        
        return list(sources.values())
    
    def _create_sourcer(self, source: Dict):
        """
        Dynamically create the appropriate sourcer based on source type.
        
        This is the extensibility point - add new sourcers here as they're implemented.
        """
        source_type = source['type'].lower()
        config = source.get('config', {})
        
        if source_type == 'rss':
            return RSSSourcer(
                feed_url=source['url'],
                name=source['name'],
                max_entries=config.get('max_entries', 200)
            )
        
        elif source_type == 'reddit':
            return RedditSourcer(
                subreddit=config.get('subreddit'),
                name=source['name'],
                limit=config.get('limit', 100),
                time_filter=config.get('time_filter', 'day'),
                sort_by=config.get('sort_by', 'hot'),
            )
        
        elif source_type == 'twitter':
            return TwitterSourcer(
                search_query=config.get('search_query'),
                username=config.get('username'),
                hashtag=config.get('hashtag'),
                name=source['name'],
                max_tweets=config.get('max_tweets', 50),
                mode=config.get('mode', 'term'),
            )
        
        elif source_type == 'youtube':
            return YouTubeSourcer(
                search_query=config.get('search_query'),
                channel_id=config.get('channel_id'),
                name=source['name'],
                max_results=config.get('max_results', 25),
                order=config.get('order', 'relevance'),
            )
        
        elif source_type == 'newsapi':
            return NewsAPISourcer(
                query=config.get('query'),
                sources=config.get('sources'),
                domains=config.get('domains'),
                category=config.get('category'),
                country=config.get('country'),
                name=source['name'],
                max_articles=config.get('max_articles', 100),
                language=config.get('language', 'en'),
            )
        
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def fetch_from_source(self, source: Dict) -> Dict:
        """Fetch data from a single source using the appropriate sourcer."""
        try:
            logger.info(f"Fetching from: {source['name']} ({source['type']})")
            
            # Create the appropriate sourcer
            sourcer = self._create_sourcer(source)
            
            # Fetch content
            contents = await sourcer.fetch()
            
            # Filter for last 7 days only
            cutoff = datetime.now() - timedelta(days=self.days_to_keep)
            recent = [c for c in contents if c.published_date and c.published_date >= cutoff]
            
            # Save to data lake
            result = self.content_repo.save_batch(
                contents=recent,
                source_type=source['type'],
                source_name=source['name'],
                source_url=source['url'],
            )
            
            logger.info(
                f"  ✓ {source['name']}: "
                f"{result['saved']} new, {result['duplicates']} duplicates, "
                f"{len(recent)} total fetched"
            )
            
            return {
                'source': source['name'],
                'type': source['type'],
                'success': True,
                'new': result['saved'],
                'duplicates': result['duplicates'],
                'total_fetched': len(recent),
            }
            
        except ImportError as e:
            logger.warning(f"  ⚠ {source['name']}: Missing dependency - {e}")
            return {
                'source': source['name'],
                'type': source['type'],
                'success': False,
                'error': f"Missing dependency: {str(e)}",
            }
        except Exception as e:
            logger.error(f"  ✗ {source['name']}: {e}")
            return {
                'source': source['name'],
                'type': source['type'],
                'success': False,
                'error': str(e),
            }
    
    async def fetch_all_sources(self):
        """Fetch from all sources concurrently."""
        sources = self.get_all_sources()
        logger.info(f"\n{'='*80}")
        logger.info(f"Fetching from {len(sources)} sources...")
        logger.info(f"{'='*80}")
        
        # Fetch concurrently
        tasks = [self.fetch_from_source(source) for source in sources]
        results = await asyncio.gather(*tasks)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        total_new = sum(r.get('new', 0) for r in results if r['success'])
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Fetch complete: {successful}/{len(sources)} successful")
        logger.info(f"Total new documents: {total_new}")
        logger.info(f"{'='*80}\n")
        
        return results
    
    def cleanup_old_data(self):
        """Remove data older than 7 days."""
        cutoff = datetime.now() - timedelta(days=self.days_to_keep + 1)  # Keep 1 extra day buffer
        
        from storage.models import SourcedContentModel
        
        old_items = self.content_repo.session.query(SourcedContentModel).filter(
            SourcedContentModel.published_date < cutoff
        ).all()
        
        if old_items:
            for item in old_items:
                self.content_repo.session.delete(item)
            self.content_repo.session.commit()
            logger.info(f"Cleaned up {len(old_items)} documents older than {self.days_to_keep} days")
    
    async def run_once(self):
        """Run one fetch cycle."""
        await self.fetch_all_sources()
        self.cleanup_old_data()
    
    async def run_forever(self):
        """Run perpetually, fetching every hour."""
        logger.info("="*80)
        logger.info("DATA SOURCING SERVICE STARTED")
        logger.info("="*80)
        logger.info(f"Fetch interval: {self.fetch_interval_seconds}s ({self.fetch_interval_seconds/3600}h)")
        logger.info(f"Data retention: {self.days_to_keep} days")
        logger.info("="*80 + "\n")
        
        while True:
            try:
                await self.run_once()
                
                # Wait for next cycle
                next_fetch = datetime.now() + timedelta(seconds=self.fetch_interval_seconds)
                logger.info(f"Next fetch at: {next_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"Waiting {self.fetch_interval_seconds}s...\n")
                
                await asyncio.sleep(self.fetch_interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("\nShutting down...")
                break
            except Exception as e:
                logger.error(f"Error in fetch cycle: {e}")
                logger.info("Waiting 60s before retry...")
                await asyncio.sleep(60)
        
        self.content_repo.close()
        self.team_repo.close()


async def main():
    """Main entry point."""
    service = DataSourcingService()
    
    # Initial fetch
    await service.run_once()
    
    # Ask if user wants to run perpetually
    print("\nRun perpetually? (y/n): ", end='', flush=True)
    choice = input().strip().lower()
    
    if choice == 'y':
        await service.run_forever()
    else:
        service.content_repo.close()
        service.team_repo.close()
        print("Exiting.")


if __name__ == "__main__":
    asyncio.run(main())
