"""Script to add all blog sources from scraping_sources.json to the database"""
import json
from storage import SourceConfigRepository

def add_all_sources():
    # Load sources from JSON
    with open('scraping_sources.json', 'r') as f:
        data = json.load(f)
    
    repo = SourceConfigRepository()
    
    total_added = 0
    total_existing = 0
    
    for team_key, team_data in data['scraping_sources'].items():
        team_name = team_data['team_name']
        blogs = team_data['blogs']
        
        print(f"\n{'='*60}")
        print(f"Processing {team_name} ({team_key})")
        print(f"{'='*60}")
        
        for blog in blogs:
            source_name = blog['name']
            source_url = blog['url']
            
            # Add source (method handles duplicates automatically)
            config = {
                'team_key': team_key,
                'team_name': team_name,
                'selectors': blog['selectors'],
                'max_pages': blog.get('max_pages', 5)
            }
            
            # Convert hours to minutes
            fetch_interval_minutes = blog['fetch_interval_hours'] * 60
            
            source = repo.add_source(
                source_type='blog_scrape',
                source_name=source_name,
                source_url=source_url,
                config=config,
                fetch_interval_minutes=fetch_interval_minutes
            )
            
            # Check if it was newly created or already existed
            if source.last_fetched_at is None:
                print(f"  ✅ {source_name} - Added (ID: {source.id})")
                total_added += 1
            else:
                print(f"  ⚠️  {source_name} - Already exists (ID: {source.id})")
                total_existing += 1
    
    repo.close()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Sources added: {total_added}")
    print(f"⚠️  Sources already existed: {total_existing}")
    print(f"📊 Total sources: {total_added + total_existing}")
    print(f"\n🎉 All sources have been added to the database!")
    print(f"🔄 The scheduler will automatically start fetching content.")

if __name__ == "__main__":
    add_all_sources()
