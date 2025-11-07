"""
Setup teams database from config.json - the single source of truth.

This script:
1. Reads team configurations from config.json
2. Creates teams database
3. Populates teams and their sources
4. Shows team statistics
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from teams.models import TeamBase, InternalTeamModel, TeamSourceModel


def get_database_url(db_name: str = "teams.db") -> str:
    """Get database URL for teams database."""
    db_path = Path(__file__).parent / "data" / db_name
    db_path.parent.mkdir(exist_ok=True)
    return f"sqlite:///{db_path}"


def create_database(db_url: str):
    """Create all tables in the database."""
    engine = create_engine(db_url, echo=False)
    TeamBase.metadata.create_all(engine)
    return engine


def load_config() -> dict:
    """Load configuration from config.json."""
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create config.json with team and source definitions."
        )
    
    with open(config_path, 'r') as f:
        return json.load(f)


async def setup_database():
    """Initialize the database with tables."""
    print("=" * 70)
    print("Setting up Teams Database")
    print("=" * 70)
    
    db_url = get_database_url()
    print(f"\nDatabase URL: {db_url}")
    
    # Create database and tables
    engine = create_database(db_url)
    print("✓ Database tables created successfully")
    
    return engine


async def populate_teams_from_config(engine):
    """Populate teams and sources from config.json."""
    print("\n" + "=" * 70)
    print("Populating Teams from config.json")
    print("=" * 70)
    
    # Load configuration
    config = load_config()
    teams_data = config.get('teams', [])
    
    if not teams_data:
        print("⚠ No teams found in config.json")
        return
    
    print(f"\nFound {len(teams_data)} teams in configuration\n")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        total_sources = 0
        
        for team_data in teams_data:
            # Create team
            team = InternalTeamModel(
                team_key=team_data['team_key'],
                team_name=team_data['team_name'],
                description=team_data.get('description', ''),
                keyword_config=team_data['keyword_config'],
                sentiment_config=team_data['sentiment_config'],
                color=team_data.get('color'),
                icon=team_data.get('icon'),
                is_active=team_data.get('is_active', True),
            )
            
            session.add(team)
            session.flush()  # Get team.id
            
            # Add sources for this team
            sources = team_data.get('sources', [])
            for source_data in sources:
                source = TeamSourceModel(
                    team_id=team.id,
                    source_type=source_data['source_type'],
                    source_name=source_data['source_name'],
                    source_url=source_data['source_url'],
                    source_config=source_data.get('config', {}),
                    fetch_interval_minutes=source_data.get('fetch_interval_minutes', 60),
                    is_enabled=True,
                )
                session.add(source)
                total_sources += 1
            
            session.commit()
            
            print(f"✓ {team.team_name} ({team.team_key})")
            print(f"  - Sources: {len(sources)}")
            print(f"  - Keyword threshold: {team.keyword_config.get('relevance_threshold', 'N/A')}")
            print(f"  - Color: {team.color}")
            print()
        
        print(f"{'=' * 70}")
        print(f"Total: {len(teams_data)} teams, {total_sources} sources")
        print(f"{'=' * 70}")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error populating teams: {e}")
        raise
    
    finally:
        session.close()


async def show_teams(engine):
    """Display all teams and their configurations."""
    print("\n" + "=" * 70)
    print("Configured Teams")
    print("=" * 70)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        teams = session.query(InternalTeamModel).all()
        
        for team in teams:
            status = "✓ Active" if team.is_active else "✗ Inactive"
            print(f"\n{status} {team.team_name} ({team.team_key})")
            print(f"  Description: {team.description}")
            print(f"  Color: {team.color}")
            print(f"  Icon: {team.icon}")
            
            # Keyword config
            kw_config = team.keyword_config
            print(f"  Keyword Config:")
            print(f"    - Threshold: {kw_config.get('relevance_threshold')}")
            print(f"    - Min Frequency: {kw_config.get('min_frequency')}")
            print(f"    - Methods: {', '.join(kw_config.get('methods', []))}")
            
            # Sources
            print(f"  Sources ({len(team.sources)}):")
            for source in team.sources:
                enabled = "✓" if source.is_enabled else "✗"
                print(f"    {enabled} {source.source_name}")
                print(f"       URL: {source.source_url}")
                print(f"       Interval: {source.fetch_interval_minutes} min")
    
    finally:
        session.close()


async def show_statistics(engine):
    """Display database statistics."""
    print("\n" + "=" * 70)
    print("Teams Database Statistics")
    print("=" * 70)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        total_teams = session.query(InternalTeamModel).count()
        active_teams = session.query(InternalTeamModel).filter_by(is_active=True).count()
        total_sources = session.query(TeamSourceModel).count()
        enabled_sources = session.query(TeamSourceModel).filter_by(is_enabled=True).count()
        
        print(f"\nTotal Teams: {total_teams}")
        print(f"Active Teams: {active_teams}")
        print(f"Total Sources: {total_sources}")
        print(f"Enabled Sources: {enabled_sources}")
        
        # Sources by team
        print("\nSources per Team:")
        teams = session.query(InternalTeamModel).all()
        for team in teams:
            source_count = len(team.sources)
            enabled_count = sum(1 for s in team.sources if s.is_enabled)
            print(f"  {team.team_name}: {enabled_count}/{source_count} enabled")
    
    finally:
        session.close()


async def validate_config():
    """Validate the configuration file."""
    print("=" * 70)
    print("Validating config.json")
    print("=" * 70)
    
    try:
        config = load_config()
        teams = config.get('teams', [])
        
        if not teams:
            print("✗ No teams defined in config.json")
            return False
        
        print(f"✓ Found {len(teams)} teams")
        
        # Validate each team
        required_team_fields = ['team_key', 'team_name', 'keyword_config', 'sentiment_config']
        required_source_fields = ['source_type', 'source_name', 'source_url']
        
        total_sources = 0
        for team in teams:
            # Check required fields
            missing = [f for f in required_team_fields if f not in team]
            if missing:
                print(f"✗ Team missing fields: {missing}")
                return False
            
            # Check sources
            sources = team.get('sources', [])
            total_sources += len(sources)
            
            for source in sources:
                missing = [f for f in required_source_fields if f not in source]
                if missing:
                    print(f"✗ Source in team '{team['team_key']}' missing fields: {missing}")
                    return False
        
        print(f"✓ All teams have required fields")
        print(f"✓ Total sources: {total_sources}")
        print("✓ Configuration is valid")
        
        return True
    
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


async def export_current_config():
    """Export current database configuration to JSON (for backup/migration)."""
    print("=" * 70)
    print("Exporting Current Configuration")
    print("=" * 70)
    
    db_url = get_database_url()
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        teams = session.query(InternalTeamModel).all()
        
        config = {
            "teams": []
        }
        
        for team in teams:
            team_data = {
                "team_key": team.team_key,
                "team_name": team.team_name,
                "description": team.description,
                "color": team.color,
                "icon": team.icon,
                "is_active": team.is_active,
                "keyword_config": team.keyword_config,
                "sentiment_config": team.sentiment_config,
                "sources": []
            }
            
            for source in team.sources:
                source_data = {
                    "source_type": source.source_type,
                    "source_name": source.source_name,
                    "source_url": source.source_url,
                    "fetch_interval_minutes": source.fetch_interval_minutes,
                    "config": source.source_config
                }
                team_data["sources"].append(source_data)
            
            config["teams"].append(team_data)
        
        # Save to backup file
        backup_path = Path(__file__).parent / "config_backup.json"
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuration exported to: {backup_path}")
        print(f"  Teams: {len(config['teams'])}")
        total_sources = sum(len(t['sources']) for t in config['teams'])
        print(f"  Total sources: {total_sources}")
    
    finally:
        session.close()


async def main():
    """Main setup function."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            await validate_config()
        
        elif command == "init":
            if await validate_config():
                engine = await setup_database()
                await populate_teams_from_config(engine)
                await show_statistics(engine)
                print("\n✓ Teams database initialized from config.json")
        
        elif command == "show":
            engine = create_engine(get_database_url(), echo=False)
            await show_teams(engine)
        
        elif command == "stats":
            engine = create_engine(get_database_url(), echo=False)
            await show_statistics(engine)
        
        elif command == "export":
            await export_current_config()
        
        else:
            print(f"Unknown command: {command}")
            print_usage()
    
    else:
        # Run full setup
        if await validate_config():
            engine = await setup_database()
            await populate_teams_from_config(engine)
            await show_teams(engine)
            await show_statistics(engine)


def print_usage():
    """Print usage instructions."""
    print("""
Usage: python setup_teams.py [command]

Commands:
  validate  - Validate config.json structure
  init      - Initialize database from config.json
  show      - Show all configured teams
  stats     - Show database statistics
  export    - Export current database to config_backup.json
  
  (no command) - Run full setup from config.json

Note: All configuration is read from config.json (single source of truth)
    """)


if __name__ == "__main__":
    asyncio.run(main())
