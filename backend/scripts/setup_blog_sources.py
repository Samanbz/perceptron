"""
Script to add all blog scraping sources to the monitoring system
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from storage import SourceConfigRepository


def load_scraping_sources():
    """Load scraping sources from JSON file"""
    config_file = Path(__file__).parent / "scraping_sources.json"
    with open(config_file, 'r') as f:
        return json.load(f)


def add_blog_sources():
    """Add all blog sources to monitoring system"""
    config = load_scraping_sources()
    repo = SourceConfigRepository()
    
    added_count = 0
    skipped_count = 0
    
    for team_key, team_data in config['scraping_sources'].items():
        print(f"\n{'='*60}")
        print(f"Processing {team_data['team_name']} ({team_key})")
        print(f"{'='*60}")
        
        for blog in team_data['blogs']:
            # Check if source already exists
            existing = repo.list_sources()
            if any(s.source_url == blog['url'] for s in existing):
                print(f"⏭️  SKIP: {blog['name']} (already exists)")
                skipped_count += 1
                continue
            
            try:
                # Add source to monitoring
                source = repo.add_source(
                    source_type="blog_scrape",
                    source_name=f"{team_key.upper()}: {blog['name']}",
                    source_url=blog['url'],
                    config={
                        'selectors': blog['selectors'],
                        'max_pages': 5,
                        'team_key': team_key
                    },
                    fetch_interval_minutes=blog['fetch_interval_hours'] * 60
                )
                
                print(f"✅ ADDED: {blog['name']}")
                print(f"   URL: {blog['url']}")
                print(f"   Fetch interval: {blog['fetch_interval_hours']} hours")
                print(f"   Source ID: {source.id}")
                added_count += 1
                
            except Exception as e:
                print(f"❌ ERROR adding {blog['name']}: {e}")
    
    repo.close()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Added: {added_count} sources")
    print(f"⏭️  Skipped: {skipped_count} sources (already exist)")
    print(f"📊 Total in config: {added_count + skipped_count}")


def list_sources():
    """List all configured scraping sources"""
    repo = SourceConfigRepository()
    sources = repo.list_sources()
    repo.close()
    
    blog_sources = [s for s in sources if s.source_type == "blog_scrape"]
    
    print(f"\n{'='*60}")
    print(f"CONFIGURED BLOG SOURCES ({len(blog_sources)})")
    print(f"{'='*60}\n")
    
    for source in blog_sources:
        status = "✅ ENABLED" if source.enabled else "❌ DISABLED"
        print(f"{status} {source.source_name}")
        print(f"   URL: {source.source_url}")
        print(f"   Interval: {source.fetch_interval_minutes} minutes")
        print(f"   Total fetched: {source.total_items_fetched}")
        if source.last_fetched_at:
            print(f"   Last fetched: {source.last_fetched_at}")
        if source.last_error:
            print(f"   ⚠️  Last error: {source.last_error}")
        print()


def remove_all_blog_sources():
    """Remove all blog scraping sources (use with caution!)"""
    response = input("Are you sure you want to remove ALL blog sources? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    repo = SourceConfigRepository()
    sources = repo.list_sources()
    
    removed_count = 0
    for source in sources:
        if source.source_type == "blog_scrape":
            # Note: Need to add delete method to repository
            print(f"Would remove: {source.source_name}")
            removed_count += 1
    
    repo.close()
    print(f"\nWould remove {removed_count} sources")
    print("(Delete functionality needs to be implemented in SourceConfigRepository)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage blog scraping sources")
    parser.add_argument('action', choices=['add', 'list', 'remove'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        add_blog_sources()
    elif args.action == 'list':
        list_sources()
    elif args.action == 'remove':
        remove_all_blog_sources()
