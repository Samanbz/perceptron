#!/usr/bin/env python3
"""
Initialize the entire system from scratch:
1. Create all database tables
2. Load teams and sources from config.json
3. Show configuration summary
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from teams.models import TeamBase, InternalTeamModel, TeamSourceModel
from storage.models import Base as StorageBase
from keywords.models import KeywordBase


def get_db_url(db_name: str) -> str:
    """Get database URL."""
    db_path = Path(__file__).parent.parent / "data" / db_name
    db_path.parent.mkdir(exist_ok=True)
    return f"sqlite:///{db_path}"


def create_all_databases():
    """Create all database tables."""
    print("\n" + "="*80)
    print("CREATING DATABASE TABLES")
    print("="*80 + "\n")
    
    # Teams database
    teams_url = get_db_url("teams.db")
    teams_engine = create_engine(teams_url, echo=False)
    TeamBase.metadata.create_all(teams_engine)
    print("✓ Created teams.db tables")
    
    # Sourcer pipeline database
    sourcer_url = get_db_url("sourcer_pipeline.db")
    sourcer_engine = create_engine(sourcer_url, echo=False)
    StorageBase.metadata.create_all(sourcer_engine)
    print("✓ Created sourcer_pipeline.db tables")
    
    # Keywords database
    keywords_url = get_db_url("keywords.db")
    keywords_engine = create_engine(keywords_url, echo=False)
    KeywordBase.metadata.create_all(keywords_engine)
    print("✓ Created keywords.db tables")
    
    return teams_engine


def load_teams_from_config(engine):
    """Load teams and sources from config.json."""
    print("\n" + "="*80)
    print("LOADING TEAMS FROM CONFIG.JSON")
    print("="*80 + "\n")
    
    # Read config
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    teams_data = config.get('teams', [])
    print(f"Loading {len(teams_data)} teams...\n")
    
    total_sources = 0
    enabled_sources = 0
    
    for team_data in teams_data:
        now = datetime.now()
        
        # Create team
        team = InternalTeamModel(
            team_key=team_data['team_key'],
            team_name=team_data['team_name'],
            description=team_data.get('description', ''),
            color=team_data.get('color', '#808080'),
            icon=team_data.get('icon', 'group'),
            is_active=team_data.get('is_active', True),
            keyword_config=json.dumps(team_data.get('keyword_config', {})),
            sentiment_config=json.dumps(team_data.get('sentiment_config', {})),
            created_at=now,
            updated_at=now
        )
        session.add(team)
        session.flush()
        
        print(f"📁 {team.team_name} ({team.team_key})")
        print(f"   {team.description}")
        
        # Add sources
        for source_data in team_data.get('sources', []):
            is_enabled = source_data.get('is_enabled', True)
            
            source = TeamSourceModel(
                team_id=team.id,
                source_type=source_data['source_type'],
                source_name=source_data['source_name'],
                source_url=source_data['source_url'],
                fetch_interval_minutes=source_data.get('fetch_interval_minutes', 60),
                is_enabled=is_enabled,
                source_config=json.dumps(source_data.get('config', {})),
                total_items_fetched=0,
                last_fetch_count=0,
                created_at=now,
                updated_at=now
            )
            session.add(source)
            
            status = "✓" if is_enabled else "✗"
            print(f"   {status} {source.source_name:30s} ({source.source_url[:50]}...)")
            
            if 'notes' in source_data:
                print(f"      📝 {source_data['notes']}")
            
            total_sources += 1
            if is_enabled:
                enabled_sources += 1
        
        print()
    
    session.commit()
    session.close()
    
    print("="*80)
    print(f"✓ Loaded {len(teams_data)} teams with {total_sources} sources ({enabled_sources} enabled)")
    print("="*80)


def show_summary():
    """Show configuration summary."""
    print("\n" + "="*80)
    print("SYSTEM INITIALIZATION COMPLETE")
    print("="*80)
    print("\n✅ All databases created and configured")
    print("\nNext steps:")
    print("  1. Fetch documents:    python scripts/fetch_all_sources.py")
    print("  2. Process keywords:   python scripts/generate_demo_data.py")
    print("  3. Start API:          python app.py")
    print()


if __name__ == "__main__":
    try:
        engine = create_all_databases()
        load_teams_from_config(engine)
        show_summary()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
