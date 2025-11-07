#!/usr/bin/env python3
"""
Setup script for keyword extraction database.

Usage:
    python setup_keywords.py init       # Initialize database
    python setup_keywords.py stats      # Show statistics
    python setup_keywords.py config     # Manage configurations
"""

import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keywords.models import (
    create_keyword_tables,
    get_keyword_session,
    KeywordExtractionConfigModel,
)
from keywords.repository import KeywordRepository, KeywordConfigRepository


def init_database():
    """Initialize the keyword database."""
    print("Initializing keyword extraction database...")
    
    # Create tables
    create_keyword_tables()
    print("✓ Tables created")
    
    # Create default configuration
    config_repo = KeywordConfigRepository()
    
    existing = config_repo.get_active_config()
    if not existing:
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
        print("✓ Default configuration created")
    else:
        print(f"✓ Active configuration found: {existing.config_name}")
    
    config_repo.close()
    
    print("\nDatabase initialized successfully!")
    print(f"Location: data/keywords.db")


def show_stats():
    """Show keyword database statistics."""
    repo = KeywordRepository()
    
    stats = repo.get_statistics()
    
    print("\n=== Keyword Database Statistics ===\n")
    print(f"Total keyword records: {stats['total_keywords']}")
    print(f"Unique keywords: {stats['unique_keywords']}")
    print(f"Today's extractions: {stats['today']}")
    
    if stats['by_source']:
        print("\nBy source:")
        for source, count in stats['by_source'].items():
            print(f"  {source}: {count}")
    
    # Show top keywords from last 7 days
    print("\nTop keywords (last 7 days, min relevance 0.7):")
    top = repo.get_top_keywords(days=7, min_relevance=0.7, limit=20)
    
    if top:
        for i, kw in enumerate(top, 1):
            print(
                f"  {i:2d}. {kw['keyword']:30s} "
                f"score={kw['max_relevance']:.3f} "
                f"freq={kw['total_frequency']:3d} "
                f"docs={kw['appearance_count']:2d}"
            )
    else:
        print("  No keywords found")
    
    repo.close()


def manage_configs():
    """Manage extraction configurations."""
    repo = KeywordConfigRepository()
    
    print("\n=== Keyword Extraction Configurations ===\n")
    
    configs = repo.list_configs()
    
    if not configs:
        print("No configurations found. Run 'init' to create default config.")
        repo.close()
        return
    
    for config in configs:
        status = "ACTIVE" if config.is_active else "inactive"
        print(f"\n{config.config_name} [{status}]")
        print(f"  Relevance threshold: {config.relevance_threshold}")
        print(f"  Weights: TF-IDF={config.tfidf_weight}, spaCy={config.spacy_weight}, YAKE={config.yake_weight}")
        print(f"  Max keywords/source: {config.max_keywords_per_source}")
        print(f"  Phrase length: {config.min_phrase_length}-{config.max_phrase_length} words")
    
    repo.close()


def create_demo_config():
    """Create a demo configuration with lower threshold."""
    repo = KeywordConfigRepository()
    
    # Check if demo config exists
    session = repo.session
    existing = session.query(KeywordExtractionConfigModel).filter(
        KeywordExtractionConfigModel.config_name == "demo"
    ).first()
    
    if existing:
        print("Demo configuration already exists")
    else:
        repo.create_config(
            config_name="demo",
            relevance_threshold=0.5,  # Lower threshold for demo
            tfidf_weight=0.3,
            spacy_weight=0.4,
            yake_weight=0.3,
            max_keywords_per_source=100,  # More keywords
            min_phrase_length=1,
            max_phrase_length=5,
            is_active=0,  # Not active by default
        )
        print("✓ Demo configuration created")
        print("  Relevance threshold: 0.5 (lower for more keywords)")
        print("  Max keywords: 100")
        print("\nTo activate: python setup_keywords.py activate demo")
    
    repo.close()


def activate_config(config_name: str):
    """Activate a specific configuration."""
    repo = KeywordConfigRepository()
    
    repo.set_active_config(config_name)
    print(f"✓ Activated configuration: {config_name}")
    
    repo.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_database()
    
    elif command == "stats":
        show_stats()
    
    elif command == "config":
        manage_configs()
    
    elif command == "demo":
        create_demo_config()
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Usage: python setup_keywords.py activate <config_name>")
            sys.exit(1)
        activate_config(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
