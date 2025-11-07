"""
Setup and manage the data lake for sourced content.

This script:
1. Creates the database
2. Adds example sources
3. Shows how to manually trigger fetches
4. Displays statistics
"""

import asyncio
from datetime import datetime, timedelta

from storage import (
    create_database,
    ContentRepository,
    SourceConfigRepository,
    get_database_url,
)
from sourcers import RSSSourcer


async def setup_database():
    """Initialize the database with tables."""
    print("=" * 70)
    print("Setting up Data Lake Database")
    print("=" * 70)
    
    db_url = get_database_url()
    print(f"\nDatabase URL: {db_url}")
    
    # Create database and tables
    create_database(db_url)
    print("✓ Database tables created successfully")


async def add_example_sources():
    """Add example RSS feed sources to monitor."""
    print("\n" + "=" * 70)
    print("Adding Example Sources")
    print("=" * 70)
    
    config_repo = SourceConfigRepository()
    
    # Example sources to monitor
    sources = [
        {
            "source_type": "rss",
            "source_name": "TechCrunch",
            "source_url": "https://techcrunch.com/feed/",
            "fetch_interval_minutes": 30,
            "config": {"max_entries": 50}
        },
        {
            "source_type": "rss",
            "source_name": "Hacker News",
            "source_url": "https://news.ycombinator.com/rss",
            "fetch_interval_minutes": 60,
            "config": {"max_entries": 30}
        },
        {
            "source_type": "rss",
            "source_name": "The Verge",
            "source_url": "https://www.theverge.com/rss/index.xml",
            "fetch_interval_minutes": 45,
            "config": {"max_entries": 40}
        },
        {
            "source_type": "rss",
            "source_name": "Ars Technica",
            "source_url": "https://feeds.arstechnica.com/arstechnica/index",
            "fetch_interval_minutes": 60,
            "config": {"max_entries": 30}
        },
    ]
    
    for source in sources:
        config = config_repo.add_source(**source)
        print(f"✓ Added: {source['source_name']} (fetch every {source['fetch_interval_minutes']} min)")
    
    config_repo.close()


async def fetch_all_sources_now():
    """Manually fetch from all configured sources."""
    print("\n" + "=" * 70)
    print("Fetching from All Configured Sources")
    print("=" * 70)
    
    content_repo = ContentRepository()
    config_repo = SourceConfigRepository()
    
    sources = config_repo.list_sources(enabled_only=True)
    print(f"\nFound {len(sources)} active sources\n")
    
    total_new = 0
    total_duplicates = 0
    
    for source in sources:
        print(f"Fetching: {source.source_name}...")
        
        # Create sourcer
        if source.source_type == 'rss':
            sourcer = RSSSourcer(
                feed_url=source.source_url,
                name=source.source_name,
                max_entries=source.config.get('max_entries', 50),
            )
        else:
            print(f"  ⚠ Unsupported source type: {source.source_type}")
            continue
        
        # Fetch content
        try:
            contents = await sourcer.fetch()
            print(f"  Fetched {len(contents)} items")
            
            # Save with deduplication
            stats = content_repo.save_batch(
                contents,
                source_type=source.source_type,
                source_name=source.source_name,
                source_url=source.source_url,
            )
            
            print(f"  ✓ Saved {stats['saved']} new, skipped {stats['duplicates']} duplicates")
            
            total_new += stats['saved']
            total_duplicates += stats['duplicates']
            
            # Update fetch status
            config_repo.update_fetch_status(source.id, stats['saved'])
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            config_repo.update_fetch_status(source.id, 0, error=str(e))
    
    print(f"\n{'=' * 70}")
    print(f"Total: {total_new} new items, {total_duplicates} duplicates")
    print(f"{'=' * 70}")
    
    content_repo.close()
    config_repo.close()


async def show_statistics():
    """Display database statistics."""
    print("\n" + "=" * 70)
    print("Data Lake Statistics")
    print("=" * 70)
    
    content_repo = ContentRepository()
    stats = content_repo.get_statistics()
    
    print(f"\nTotal Content Items: {stats['total_content']}")
    print(f"Processed: {stats['processed']}")
    print(f"Unprocessed (ready for NLP): {stats['unprocessed']}")
    
    print("\nContent by Source Type:")
    for source_type, count in stats['by_source_type'].items():
        print(f"  {source_type}: {count}")
    
    content_repo.close()


async def show_recent_content(limit: int = 10):
    """Show recently fetched content."""
    print("\n" + "=" * 70)
    print(f"Recent Content (last {limit} items)")
    print("=" * 70)
    
    content_repo = ContentRepository()
    
    # Get content from last 7 days
    start_date = datetime.now() - timedelta(days=7)
    contents = content_repo.get_content_by_date_range(start_date)
    
    for i, content in enumerate(contents[:limit], 1):
        print(f"\n{i}. {content.title}")
        print(f"   Source: {content.source_name} ({content.source_type})")
        print(f"   Published: {content.published_date}")
        print(f"   URL: {content.url}")
        print(f"   Processed: {'Yes' if content.processed else 'No'}")
    
    content_repo.close()


async def list_sources():
    """List all configured sources."""
    print("\n" + "=" * 70)
    print("Configured Sources")
    print("=" * 70)
    
    config_repo = SourceConfigRepository()
    sources = config_repo.list_sources()
    
    for source in sources:
        status = "✓ Enabled" if source.enabled else "✗ Disabled"
        print(f"\n{status} {source.source_name}")
        print(f"  Type: {source.source_type}")
        print(f"  URL: {source.source_url}")
        print(f"  Fetch Interval: {source.fetch_interval_minutes} minutes")
        print(f"  Total Items Fetched: {source.total_items_fetched}")
        print(f"  Last Fetched: {source.last_fetched_at or 'Never'}")
        print(f"  Next Fetch: {source.next_fetch_at or 'Not scheduled'}")
        if source.last_error:
            print(f"  Last Error: {source.last_error}")
    
    config_repo.close()


async def main():
    """Main setup and demo function."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            await setup_database()
            await add_example_sources()
            print("\n✓ Database initialized with example sources")
        
        elif command == "fetch":
            await fetch_all_sources_now()
        
        elif command == "stats":
            await show_statistics()
        
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            await show_recent_content(limit)
        
        elif command == "sources":
            await list_sources()
        
        else:
            print(f"Unknown command: {command}")
            print_usage()
    
    else:
        # Run full setup
        await setup_database()
        await add_example_sources()
        await fetch_all_sources_now()
        await show_statistics()
        await show_recent_content(5)


def print_usage():
    """Print usage instructions."""
    print("""
Usage: python setup_data_lake.py [command]

Commands:
  init      - Initialize database and add example sources
  fetch     - Fetch from all configured sources now
  stats     - Show database statistics
  recent [N] - Show N recent content items (default: 10)
  sources   - List all configured sources
  
  (no command) - Run full setup and initial fetch
    """)


if __name__ == "__main__":
    asyncio.run(main())
