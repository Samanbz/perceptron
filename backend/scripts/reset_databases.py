#!/usr/bin/env python3
"""
Utility to reset all databases (data lake and keywords).

Usage:
    python reset_databases.py          # Interactive confirmation
    python reset_databases.py --force  # Skip confirmation
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def reset_all_databases(force: bool = False):
    """
    Reset all databases by deleting and recreating them.
    
    Args:
        force: Skip confirmation if True
    """
    data_dir = Path("data")
    
    # Database files
    datalake_db = data_dir / "sourcer_pipeline.db"
    keywords_db = data_dir / "keywords.db"
    
    # Check what exists
    datalake_exists = datalake_db.exists()
    keywords_exists = keywords_db.exists()
    
    if not datalake_exists and not keywords_exists:
        print("No databases found. Nothing to reset.")
        return
    
    # Show what will be deleted
    print("\n" + "="*70)
    print("DATABASE RESET UTILITY")
    print("="*70 + "\n")
    
    if datalake_exists:
        size = datalake_db.stat().st_size / 1024  # KB
        print(f"⚠️  Data Lake: {datalake_db} ({size:.1f} KB)")
    
    if keywords_exists:
        size = keywords_db.stat().st_size / 1024  # KB
        print(f"⚠️  Keywords: {keywords_db} ({size:.1f} KB)")
    
    print("\n" + "="*70)
    print("WARNING: This will DELETE all data in these databases!")
    print("="*70 + "\n")
    
    # Confirmation
    if not force:
        response = input("Type 'yes' to confirm reset: ")
        if response.lower() != 'yes':
            print("\n❌ Reset cancelled.")
            return
    
    # Delete databases
    deleted_count = 0
    
    if datalake_exists:
        try:
            datalake_db.unlink()
            print(f"✓ Deleted {datalake_db}")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Failed to delete {datalake_db}: {e}")
    
    if keywords_exists:
        try:
            keywords_db.unlink()
            print(f"✓ Deleted {keywords_db}")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Failed to delete {keywords_db}: {e}")
    
    print(f"\n✓ Deleted {deleted_count} database(s)")
    
    # Recreate databases
    print("\nRecreating databases...\n")
    
    # Recreate data lake
    try:
        from storage.models import create_tables
        create_tables()
        print("✓ Data lake database recreated")
        
        # Add default sources
        from storage.repository import SourceConfigRepository
        repo = SourceConfigRepository()
        
        sources = [
            {
                'name': 'TechCrunch',
                'source_type': 'rss',
                'config': {'url': 'https://techcrunch.com/feed/'},
                'fetch_interval_minutes': 30
            },
            {
                'name': 'Hacker News',
                'source_type': 'rss',
                'config': {'url': 'https://news.ycombinator.com/rss'},
                'fetch_interval_minutes': 60
            },
            {
                'name': 'The Verge',
                'source_type': 'rss',
                'config': {'url': 'https://www.theverge.com/rss/index.xml'},
                'fetch_interval_minutes': 45
            },
            {
                'name': 'Ars Technica',
                'source_type': 'rss',
                'config': {'url': 'https://feeds.arstechnica.com/arstechnica/index'},
                'fetch_interval_minutes': 60
            }
        ]
        
        for source in sources:
            repo.save_source_config(**source)
        
        print(f"✓ Added {len(sources)} default RSS sources")
        repo.close()
        
    except Exception as e:
        print(f"✗ Failed to recreate data lake: {e}")
    
    # Recreate keywords database
    try:
        from keywords.models import create_keyword_tables
        from keywords.repository import KeywordConfigRepository
        
        create_keyword_tables()
        print("✓ Keywords database recreated")
        
        # Add default config
        config_repo = KeywordConfigRepository()
        config_repo.create_config(
            config_name="default",
            relevance_threshold=0.7,
            tfidf_weight=0.3,
            spacy_weight=0.4,
            yake_weight=0.3,
            max_keywords_per_source=50,
            min_phrase_length=1,
            max_phrase_length=2,
            is_active=1,
        )
        print("✓ Created default keyword extraction config")
        config_repo.close()
        
    except Exception as e:
        print(f"✗ Failed to recreate keywords database: {e}")
    
    print("\n" + "="*70)
    print("✓ Database reset complete!")
    print("="*70 + "\n")
    print("Next steps:")
    print("  1. Fetch content: python setup_data_lake.py fetch")
    print("  2. Extract keywords: python demo_keyword_pipeline.py")
    print()


def main():
    """Main entry point."""
    force = '--force' in sys.argv or '-f' in sys.argv
    reset_all_databases(force=force)


if __name__ == "__main__":
    main()
