"""Script to trigger immediate fetch for all sources"""
from datetime import datetime
from storage import SourceConfigRepository

def trigger_all_sources():
    repo = SourceConfigRepository()
    
    # Get all sources
    all_sources = repo.list_sources()
    
    print(f"Found {len(all_sources)} sources")
    print(f"Setting next_fetch_at to NOW for immediate fetching...\n")
    
    # Update all sources to fetch immediately
    for source in all_sources:
        source.next_fetch_at = datetime.utcnow()
        repo.session.add(source)
    
    repo.session.commit()
    repo.close()
    
    print(f"✅ All {len(all_sources)} sources have been scheduled for immediate fetch!")
    print(f"🔄 The scheduler will start fetching content in the next cycle (within 60 seconds).")
    print(f"\nYou can monitor the progress in the backend server logs.")

if __name__ == "__main__":
    trigger_all_sources()
