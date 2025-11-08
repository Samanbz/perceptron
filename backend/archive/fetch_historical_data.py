"""
Fetch historical RSS data to populate the data lake.

Fetches more entries from each RSS feed to get ~30 days of historical data.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.repository import ContentRepository, SourceConfigRepository
from sourcers.rss_sourcer import RSSSourcer
from teams.repository import TeamRepository


async def fetch_historical_data(days_back: int = 30):
    """
    Fetch historical data from all RSS sources.
    
    Args:
        days_back: How many days of history to try to fetch (feeds may not have this much)
    """
    
    print("=" * 80)
    print(f"FETCHING HISTORICAL RSS DATA (last {days_back} days)")
    print("=" * 80)
    
    content_repo = ContentRepository()
    team_repo = TeamRepository()
    
    # Get all teams and their sources
    teams = team_repo.get_all_teams()
    
    # Collect all unique sources across all teams
    all_sources = {}
    for team in teams:
        for source in team.sources:
            if source.is_enabled:
                key = (source.source_name, source.source_url)
                if key not in all_sources:
                    all_sources[key] = {
                        'name': source.source_name,
                        'url': source.source_url,
                        'type': source.source_type,
                        'config': source.source_config or {},
                    }
    
    print(f"\nFound {len(all_sources)} unique sources across all teams")
    print()
    
    total_fetched = 0
    total_new = 0
    total_duplicates = 0
    
    for (source_name, source_url), source_data in all_sources.items():
        print(f"Fetching from: {source_name}")
        print(f"  URL: {source_url}")
        
        try:
            # Increase max_entries to get more historical data
            # Most RSS feeds contain 20-100 items
            max_entries = 200  # Try to get as much as possible
            
            sourcer = RSSSourcer(
                feed_url=source_url,
                name=source_name,
                max_entries=max_entries
            )
            
            contents = await sourcer.fetch()
            
            # Filter for items within date range
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_contents = [
                c for c in contents 
                if c.published_date and c.published_date >= cutoff_date
            ]
            
            print(f"  Fetched: {len(contents)} total, {len(recent_contents)} within last {days_back} days")
            
            # Save to data lake
            result = content_repo.save_batch(
                contents=recent_contents,
                source_type=source_data['type'],
                source_name=source_name,
                source_url=source_url,
            )
            
            print(f"  Saved: {result['saved']} new, {result['duplicates']} duplicates")
            
            total_fetched += len(contents)
            total_new += result['saved']
            total_duplicates += result['duplicates']
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    # Get final statistics
    stats = content_repo.get_statistics()
    
    print("=" * 80)
    print("FETCH COMPLETE")
    print("=" * 80)
    print(f"\nSession Results:")
    print(f"  Total items fetched: {total_fetched}")
    print(f"  New items stored: {total_new}")
    print(f"  Duplicates skipped: {total_duplicates}")
    
    print(f"\nData Lake Statistics:")
    print(f"  Total documents: {stats['total_content']}")
    print(f"  Processed: {stats['processed']}")
    print(f"  Unprocessed: {stats['unprocessed']}")
    print(f"  By source type: {dict(stats.get('by_source_type', {}))}")
    
    # Show date range
    if stats['total_content'] > 0:
        # Get oldest and newest
        from storage.models import SourcedContentModel
        oldest = content_repo.session.query(SourcedContentModel).filter(
            SourcedContentModel.published_date.isnot(None)
        ).order_by(SourcedContentModel.published_date.asc()).first()
        
        newest = content_repo.session.query(SourcedContentModel).filter(
            SourcedContentModel.published_date.isnot(None)
        ).order_by(SourcedContentModel.published_date.desc()).first()
        
        if oldest and newest:
            print(f"\nDate Range:")
            print(f"  Oldest: {oldest.published_date.strftime('%Y-%m-%d')}")
            print(f"  Newest: {newest.published_date.strftime('%Y-%m-%d')}")
            days_span = (newest.published_date - oldest.published_date).days
            print(f"  Span: {days_span} days")
    
    content_repo.close()
    team_repo.close()
    
    print("\n✓ Historical data fetch complete!")
    
    if total_new > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Process the new content:")
        print(f"      python scripts/process_all_content.py process")
        print(f"   2. View keywords for each team:")
        print(f"      python scripts/process_all_content.py show --team regulator")


async def add_more_sources():
    """
    Add additional high-quality RSS sources to teams.
    """
    
    print("=" * 80)
    print("ADDING MORE DATA SOURCES")
    print("=" * 80)
    
    team_repo = TeamRepository()
    
    # Additional sources to add
    additional_sources = {
        'regulator': [
            {
                'source_name': 'FTC News',
                'source_url': 'https://www.ftc.gov/news-events/news/press-releases?items_per_page=50',
                'source_type': 'rss',
            },
            {
                'source_name': 'CFTC Press Releases',
                'source_url': 'https://www.cftc.gov/rss/PressReleases.xml',
                'source_type': 'rss',
            },
        ],
        'investor': [
            {
                'source_name': 'VentureBeat',
                'source_url': 'https://venturebeat.com/feed/',
                'source_type': 'rss',
            },
            {
                'source_name': 'Business Insider Tech',
                'source_url': 'https://www.businessinsider.com/sai/rss',
                'source_type': 'rss',
            },
            {
                'source_name': 'The Verge',
                'source_url': 'https://www.theverge.com/rss/index.xml',
                'source_type': 'rss',
            },
        ],
        'competitor': [
            {
                'source_name': 'TechMeme',
                'source_url': 'https://www.techmeme.com/feed.xml',
                'source_type': 'rss',
            },
            {
                'source_name': 'Product Hunt',
                'source_url': 'https://www.producthunt.com/feed',
                'source_type': 'rss',
            },
        ],
        'researcher': [
            {
                'source_name': 'MIT Technology Review',
                'source_url': 'https://www.technologyreview.com/feed/',
                'source_type': 'rss',
            },
            {
                'source_name': 'Nature News',
                'source_url': 'https://www.nature.com/nature.rss',
                'source_type': 'rss',
            },
        ],
    }
    
    for team_key, sources in additional_sources.items():
        team = team_repo.get_team_by_key(team_key)
        if not team:
            print(f"⚠️  Team {team_key} not found")
            continue
        
        print(f"\n{team.team_name} ({team_key}):")
        
        for source_data in sources:
            # Check if source already exists
            existing = any(
                s.source_name == source_data['source_name'] 
                for s in team.sources
            )
            
            if existing:
                print(f"  ⊗ {source_data['source_name']} (already exists)")
                continue
            
            try:
                team_repo.add_source_to_team(
                    team_id=team.id,
                    source_type=source_data['source_type'],
                    source_name=source_data['source_name'],
                    source_url=source_data['source_url'],
                    fetch_interval_minutes=60,
                )
                print(f"  ✓ {source_data['source_name']} added")
            except Exception as e:
                print(f"  ❌ {source_data['source_name']}: {e}")
    
    team_repo.close()
    print("\n✓ Sources updated!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch historical RSS data")
    parser.add_argument(
        'command',
        choices=['fetch', 'add-sources', 'both'],
        help='fetch: Get historical data | add-sources: Add more RSS feeds | both: Do both'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='How many days of history to fetch (default: 30)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'add-sources':
        asyncio.run(add_more_sources())
    elif args.command == 'fetch':
        asyncio.run(fetch_historical_data(args.days))
    elif args.command == 'both':
        asyncio.run(add_more_sources())
        print("\n")
        asyncio.run(fetch_historical_data(args.days))
