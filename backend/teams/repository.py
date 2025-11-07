"""
Repository for accessing team configurations from the database.

This provides a clean interface to query teams and their sources
after they've been loaded from config.json.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

from teams.models import InternalTeamModel, TeamSourceModel


def get_database_url(db_name: str = "teams.db") -> str:
    """Get database URL for teams database."""
    db_path = Path(__file__).parent.parent / "data" / db_name
    return f"sqlite:///{db_path}"


class TeamRepository:
    """Repository for team configuration operations."""
    
    def __init__(self, db_url: Optional[str] = None):
        """Initialize repository with database connection."""
        self.db_url = db_url or get_database_url()
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def get_all_teams(self, active_only: bool = True) -> List[InternalTeamModel]:
        """
        Get all teams.
        
        Args:
            active_only: If True, only return active teams
            
        Returns:
            List of team models
        """
        session = self._get_session()
        try:
            query = session.query(InternalTeamModel)
            if active_only:
                query = query.filter_by(is_active=True)
            
            # Eagerly load sources to avoid detached instance errors
            teams = query.all()
            for team in teams:
                # Force load sources while session is active
                _ = team.sources
            
            return teams
        finally:
            session.close()
    
    def get_team_by_key(self, team_key: str) -> Optional[InternalTeamModel]:
        """
        Get a team by its key.
        
        Args:
            team_key: Team key (e.g., 'regulator', 'investor')
            
        Returns:
            Team model or None if not found
        """
        session = self._get_session()
        try:
            return session.query(InternalTeamModel).filter_by(
                team_key=team_key
            ).first()
        finally:
            session.close()
    
    def get_team_by_id(self, team_id: int) -> Optional[InternalTeamModel]:
        """
        Get a team by its ID.
        
        Args:
            team_id: Team database ID
            
        Returns:
            Team model or None if not found
        """
        session = self._get_session()
        try:
            return session.query(InternalTeamModel).filter_by(
                id=team_id
            ).first()
        finally:
            session.close()
    
    def get_team_sources(
        self,
        team_key: str,
        enabled_only: bool = True
    ) -> List[TeamSourceModel]:
        """
        Get all sources for a team.
        
        Args:
            team_key: Team key
            enabled_only: If True, only return enabled sources
            
        Returns:
            List of source models
        """
        session = self._get_session()
        try:
            team = session.query(InternalTeamModel).filter_by(
                team_key=team_key
            ).first()
            
            if not team:
                return []
            
            sources = team.sources
            if enabled_only:
                sources = [s for s in sources if s.is_enabled]
            
            return sources
        finally:
            session.close()
    
    def get_sources_to_fetch(self) -> List[tuple[InternalTeamModel, TeamSourceModel]]:
        """
        Get all sources that are due for fetching.
        
        Returns:
            List of (team, source) tuples ready to fetch
        """
        session = self._get_session()
        try:
            now = datetime.utcnow()
            results = []
            
            teams = session.query(InternalTeamModel).filter_by(
                is_active=True
            ).all()
            
            for team in teams:
                for source in team.sources:
                    if not source.is_enabled:
                        continue
                    
                    # Check if it's time to fetch
                    if source.next_fetch_at is None or source.next_fetch_at <= now:
                        results.append((team, source))
            
            return results
        finally:
            session.close()
    
    def update_source_fetch_status(
        self,
        source_id: int,
        items_fetched: int,
        error: Optional[str] = None
    ):
        """
        Update source fetch statistics.
        
        Args:
            source_id: Source database ID
            items_fetched: Number of items fetched
            error: Error message if fetch failed
        """
        session = self._get_session()
        try:
            source = session.query(TeamSourceModel).filter_by(
                id=source_id
            ).first()
            
            if source:
                source.last_fetched_at = datetime.utcnow()
                source.total_items_fetched += items_fetched
                
                # Calculate next fetch time
                source.next_fetch_at = datetime.utcnow() + timedelta(
                    minutes=source.fetch_interval_minutes
                )
                
                # Store error if any
                if error:
                    source.last_error = error
                else:
                    source.last_error = None
                
                session.commit()
        finally:
            session.close()
    
    def get_keyword_config(self, team_key: str) -> Optional[dict]:
        """
        Get keyword extraction configuration for a team.
        
        Args:
            team_key: Team key
            
        Returns:
            Keyword config dict or None
        """
        team = self.get_team_by_key(team_key)
        return team.keyword_config if team else None
    
    def get_sentiment_config(self, team_key: str) -> Optional[dict]:
        """
        Get sentiment analysis configuration for a team.
        
        Args:
            team_key: Team key
            
        Returns:
            Sentiment config dict or None
        """
        team = self.get_team_by_key(team_key)
        return team.sentiment_config if team else None
    
    def get_team_list_for_api(self) -> List[dict]:
        """
        Get simplified team list for API responses.
        
        Returns:
            List of team dicts with basic info
        """
        teams = self.get_all_teams(active_only=True)
        
        return [
            {
                "team_key": team.team_key,
                "team_name": team.team_name,
                "description": team.description,
                "color": team.color,
                "icon": team.icon,
                "source_count": len([s for s in team.sources if s.is_enabled])
            }
            for team in teams
        ]
    
    def get_statistics(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Statistics dict
        """
        session = self._get_session()
        try:
            total_teams = session.query(InternalTeamModel).count()
            active_teams = session.query(InternalTeamModel).filter_by(
                is_active=True
            ).count()
            total_sources = session.query(TeamSourceModel).count()
            enabled_sources = session.query(TeamSourceModel).filter_by(
                is_enabled=True
            ).count()
            
            return {
                "total_teams": total_teams,
                "active_teams": active_teams,
                "total_sources": total_sources,
                "enabled_sources": enabled_sources,
            }
        finally:
            session.close()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Convenience function for getting team config
def get_team_config(team_key: str) -> Optional[dict]:
    """
    Get complete team configuration.
    
    Args:
        team_key: Team key (e.g., 'regulator')
        
    Returns:
        Dict with team info, keyword config, sentiment config, and sources
    """
    repo = TeamRepository()
    try:
        session = repo._get_session()
        try:
            team = session.query(InternalTeamModel).filter_by(
                team_key=team_key
            ).first()
            
            if not team:
                return None
            
            # Force load sources while session is active
            sources = team.sources
            
            result = {
                "team_key": team.team_key,
                "team_name": team.team_name,
                "description": team.description,
                "color": team.color,
                "icon": team.icon,
                "keyword_config": team.keyword_config,
                "sentiment_config": team.sentiment_config,
                "sources": [
                    {
                        "source_name": s.source_name,
                        "source_url": s.source_url,
                        "source_type": s.source_type,
                        "fetch_interval_minutes": s.fetch_interval_minutes,
                        "is_enabled": s.is_enabled,
                    }
                    for s in sources
                ]
            }
            
            return result
        finally:
            session.close()
    finally:
        repo.close()
