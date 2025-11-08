#!/usr/bin/env python3
"""
Fetch content from all configured RSS sources.

This populates the data lake with content from all teams' sources.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.repository import ContentRepository
from sourcers.rss_sourcer import RSSSourcer
from teams.repository import TeamRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


async def fetch_all_sources(max_entries_per_source: int = 50, days_back: int = 7):
    """
    Fetch content from all configured sources.
    
    Args:
        max_entries_per_source: Maximum entries to fetch per source
        days_back: Only keep content from last N days
    """
    logger.info("=" * 80)
    logger.info("FETCHING FROM ALL CONFIGURED SOURCES")
    logger.info("=" * 80)
    logger.info(f"Max entries per source: {max_entries_per_source}")
    logger.info(f"Days back: {days_back}")
    logger.info("")
    
    content_repo = ContentRepository()
    team_repo = TeamRepository()
    
    # Get all teams and their sources
    teams = team_repo.get_all_teams()
    
    # Collect unique sources across all teams
    sources_to_fetch = {}
    for team in teams:
        logger.info(f"Team: {team.team_name}")
        for source in team.sources:
            if source.is_enabled:
                key = (source.source_name, source.source_url)
                if key not in sources_to_fetch:
                    sources_to_fetch[key] = {
                        'name': source.source_name,
                        'url': source.source_url,
                        'type': source.source_type,
                        'teams': [team.team_name]
                    }
                else:
                    sources_to_fetch[key]['teams'].append(team.team_name)
                logger.info(f"  • {source.source_name}")
        logger.info("")
    
    logger.info(f"Found {len(sources_to_fetch)} unique sources to fetch from")
    logger.info("")
    
    # Fetch from each source
    total_new = 0
    total_duplicates = 0
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    for idx, ((source_name, source_url), source_info) in enumerate(sources_to_fetch.items(), 1):
        logger.info(f"[{idx}/{len(sources_to_fetch)}] Fetching: {source_name}")
        logger.info(f"  URL: {source_url}")
        logger.info(f"  Used by: {', '.join(source_info['teams'])}")
        
        try:
            sourcer = RSSSourcer(
                feed_url=source_url,
                name=source_name,
                max_entries=max_entries_per_source
            )
            
            contents = await sourcer.fetch()
            
            # Filter for recent content only
            recent_contents = [
                c for c in contents 
                if c.published_date and c.published_date >= cutoff_date
            ]
            
            logger.info(f"  Fetched {len(contents)} entries, {len(recent_contents)} recent")
            
            # Save to data lake
            if recent_contents:
                result = content_repo.save_batch(
                    contents=recent_contents,
                    source_type=source_info['type'],
                    source_name=source_name,
                    source_url=source_url,
                )
                
                total_new += result['saved']
                total_duplicates += result['duplicates']
                
                logger.info(f"  ✓ Saved {result['saved']} new, {result['duplicates']} duplicates")
            else:
                logger.info(f"  ℹ No recent content")
                
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
        
        logger.info("")
    
    content_repo.close()
    
    logger.info("=" * 80)
    logger.info("FETCH COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total new documents: {total_new}")
    logger.info(f"Total duplicates: {total_duplicates}")
    logger.info("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch content from all configured sources')
    parser.add_argument(
        '--max-entries',
        type=int,
        default=50,
        help='Maximum entries per source (default: 50)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Only fetch content from last N days (default: 7)'
    )
    
    args = parser.parse_args()
    
    asyncio.run(fetch_all_sources(
        max_entries_per_source=args.max_entries,
        days_back=args.days
    ))
