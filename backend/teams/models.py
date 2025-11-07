"""
Team-based configuration models.

Single source of truth for:
- Internal teams (regulators, investors, competitors, etc.)
- Team-specific source configurations
- Team-specific keyword extraction configs
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Float,
    JSON,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

TeamBase = declarative_base()


class InternalTeamModel(TeamBase):
    """
    Internal teams that use the system.
    
    Each team has its own:
    - Source configurations (which RSS feeds to monitor)
    - Keyword extraction settings (relevance thresholds, etc.)
    - Sentiment analysis parameters
    """
    
    __tablename__ = "internal_teams"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_key = Column(String(50), nullable=False, unique=True, index=True)  # 'regulator', 'investor', etc.
    team_name = Column(String(200), nullable=False)  # 'Regulatory Team', 'Investment Team'
    description = Column(Text, nullable=True)
    
    # Team-specific settings
    keyword_config = Column(JSON, nullable=False)  # Keyword extraction parameters
    sentiment_config = Column(JSON, nullable=False)  # Sentiment analysis parameters
    
    # Display settings
    color = Column(String(20), nullable=True)  # UI color for word cloud
    icon = Column(String(50), nullable=True)   # UI icon
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sources = relationship("TeamSourceModel", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InternalTeam(key='{self.team_key}', name='{self.team_name}')>"


class TeamSourceModel(TeamBase):
    """
    RSS/data sources assigned to specific teams.
    
    A source can belong to multiple teams.
    """
    
    __tablename__ = "team_sources"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Team relationship
    team_id = Column(Integer, ForeignKey('internal_teams.id'), nullable=False, index=True)
    
    # Source details
    source_type = Column(String(50), nullable=False)  # 'rss', 'web', 'api'
    source_name = Column(String(200), nullable=False)
    source_url = Column(Text, nullable=False)
    source_config = Column(JSON, nullable=True)  # Source-specific config
    
    # Fetching settings
    fetch_interval_minutes = Column(Integer, default=60, nullable=False)
    next_fetch_at = Column(DateTime, nullable=True)
    last_fetched_at = Column(DateTime, nullable=True)
    
    # Status
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # Fetch statistics
    total_items_fetched = Column(Integer, default=0, nullable=False)
    last_fetch_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("InternalTeamModel", back_populates="sources")
    
    # Indexes
    __table_args__ = (
        Index('idx_team_source', 'team_id', 'source_name'),
    )
    
    def __repr__(self):
        return f"<TeamSource(team_id={self.team_id}, source='{self.source_name}')>"


def get_team_database_url(db_path: str = "data/teams.db") -> str:
    """Get database URL for team configurations."""
    import os
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return f"sqlite:///{db_path}"


def get_team_session(db_url: str = None):
    """
    Create a database session for team configurations.
    
    Args:
        db_url: Database URL (defaults to teams.db)
    
    Returns:
        SQLAlchemy session
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    if db_url is None:
        db_url = get_team_database_url()
    
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def create_team_tables(db_url: str = None):
    """
    Create all team configuration tables.
    
    Args:
        db_url: Database URL (defaults to teams.db)
    """
    from sqlalchemy import create_engine
    
    if db_url is None:
        db_url = get_team_database_url()
    
    engine = create_engine(db_url, echo=False)
    TeamBase.metadata.create_all(engine)
