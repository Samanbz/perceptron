#!/usr/bin/env python3
"""
Reload teams and sources from config.json WITHOUT deleting existing data.
This updates the teams database to match the current config.json configuration.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from teams.models import TeamBase, InternalTeamModel, TeamSourceModel


def get_db_url(db_name: str) -> str:
    """Get database URL."""
    db_path = Path(__file__).parent / "data" / db_name
    db_path.parent.mkdir(exist_ok=True)
    return f"sqlite:///{db_path}"


def reload_teams_from_config():
    """Reload teams and sources from config.json."""
    print("\n" + "="*80)
    print("RELOADING TEAMS FROM CONFIG.JSON")
    print("="*80 + "\n")
    
    # Read config
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    # Create session
    teams_url = get_db_url("teams.db")
    engine = create_engine(teams_url, echo=False)
    TeamBase.metadata.create_all(engine)  # Ensure tables exist
    Session = sessionmaker(bind=engine)
    session = Session()
    
    teams_data = config.get('teams', [])
    print(f"Processing {len(teams_data)} teams from config...\n")
    
    total_sources = 0
    enabled_sources = 0
    source_type_counts = {}
    
    for team_data in teams_data:
        now = datetime.now()
        team_key = team_data['team_key']
        
        # Find or create team
        team = session.query(InternalTeamModel).filter_by(team_key=team_key).first()
        if not team:
            team = InternalTeamModel(
                team_key=team_key,
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
            print(f"🆕 Created team: {team.team_name} ({team.team_key})")
        else:
            # Update team info
            team.team_name = team_data['team_name']
            team.description = team_data.get('description', '')
            team.is_active = team_data.get('is_active', True)
            team.updated_at = now
            print(f"♻️  Updated team: {team.team_name} ({team.team_key})")
        
        session.flush()
        
        # Clear existing sources and re-add from config
        session.query(TeamSourceModel).filter_by(team_id=team.id).delete()
        
        print(f"   Sources:")
        team_type_counts = {}
        
        # Add sources from config
        for source_data in team_data.get('sources', []):
            is_enabled = source_data.get('is_enabled', True)
            source_type = source_data['source_type']
            
            source = TeamSourceModel(
                team_id=team.id,
                source_type=source_type,
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
            
            status = "✅" if is_enabled else "❌"
            print(f"   {status} [{source_type:8s}] {source.source_name}")
            
            total_sources += 1
            if is_enabled:
                enabled_sources += 1
            
            # Count source types
            team_type_counts[source_type] = team_type_counts.get(source_type, 0) + 1
            source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1
        
        print(f"   📊 Source types: {team_type_counts}")
        print()
    
    session.commit()
    session.close()
    
    print("="*80)
    print(f"✅ Reloaded {len(teams_data)} teams with {total_sources} sources ({enabled_sources} enabled)")
    print(f"📊 Source type distribution: {source_type_counts}")
    print("="*80)
    print("\nNext steps:")
    print("  1. Fetch multi-source data:  python populate_multi_source_data.py")
    print("  2. Query keywords:           python query_multi_source_keywords.py")
    print()


if __name__ == "__main__":
    try:
        reload_teams_from_config()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
