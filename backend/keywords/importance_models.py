"""
Enhanced keyword models with importance and sentiment tracking.

Extends the keyword extraction system to track:
- Keyword importance (based on multiple signals)
- Sentiment around keywords
- Time-series data for trends
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Float,
    JSON,
    DateTime,
    Index,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base

# Use existing KeywordBase or create new
from keywords.models import KeywordBase


class KeywordImportanceModel(KeywordBase):
    """
    Tracks keyword importance over time.
    
    Importance is calculated from multiple signals:
    - Frequency (how often mentioned)
    - Velocity (rate of change in mentions)
    - Source diversity (mentioned across different sources)
    - Recency (more recent = more important)
    - Sentiment intensity (stronger sentiment = more important)
    """
    
    __tablename__ = "keyword_importance"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Keyword details
    keyword = Column(String(200), nullable=False, index=True)
    keyword_normalized = Column(String(200), nullable=False, index=True)  # Lowercase, stemmed
    
    # Time dimension
    date = Column(Date, nullable=False, index=True)
    
    # Team dimension
    team_id = Column(Integer, nullable=True, index=True)  # NULL = global/all teams
    team_key = Column(String(50), nullable=True, index=True)
    
    # Source dimension
    source_type = Column(String(50), nullable=True)
    source_name = Column(String(200), nullable=True)
    
    # Importance signals
    frequency = Column(Integer, default=0, nullable=False)  # Raw mention count
    document_count = Column(Integer, default=0, nullable=False)  # Number of docs mentioning it
    source_diversity = Column(Integer, default=0, nullable=False)  # Number of different sources
    
    # Velocity (trend)
    velocity = Column(Float, default=0.0, nullable=False)  # Rate of change vs previous day
    acceleration = Column(Float, default=0.0, nullable=False)  # Change in velocity
    
    # Combined importance score (0-100)
    importance_score = Column(Float, nullable=False, index=True)
    
    # Sentiment
    sentiment_score = Column(Float, default=0.0, nullable=False)  # -1 (negative) to +1 (positive)
    sentiment_magnitude = Column(Float, default=0.0, nullable=False)  # 0-1 (strength of sentiment)
    positive_mentions = Column(Integer, default=0, nullable=False)
    negative_mentions = Column(Integer, default=0, nullable=False)
    neutral_mentions = Column(Integer, default=0, nullable=False)
    
    # References
    content_ids = Column(JSON, nullable=True)  # List of content IDs
    sample_snippets = Column(JSON, nullable=True)  # Sample text snippets showing keyword
    
    # Metadata
    extraction_method = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_keyword_date_team', 'keyword', 'date', 'team_id'),
        Index('idx_team_date_importance', 'team_id', 'date', 'importance_score'),
        Index('idx_date_importance', 'date', 'importance_score'),
    )
    
    def __repr__(self):
        return f"<KeywordImportance(keyword='{self.keyword}', date={self.date}, importance={self.importance_score:.1f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'keyword': self.keyword,
            'date': self.date.isoformat(),
            'team_key': self.team_key,
            'importance': round(self.importance_score, 2),
            'sentiment': {
                'score': round(self.sentiment_score, 3),
                'magnitude': round(self.sentiment_magnitude, 3),
                'breakdown': {
                    'positive': self.positive_mentions,
                    'negative': self.negative_mentions,
                    'neutral': self.neutral_mentions,
                }
            },
            'metrics': {
                'frequency': self.frequency,
                'document_count': self.document_count,
                'source_diversity': self.source_diversity,
                'velocity': round(self.velocity, 2),
            },
            'content_ids': self.content_ids or [],
            'sample_snippets': self.sample_snippets or [],
        }


class KeywordTimeSeriesModel(KeywordBase):
    """
    Aggregated time-series data for keywords.
    
    Pre-computed for efficient word cloud rendering.
    """
    
    __tablename__ = "keyword_timeseries"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Keyword
    keyword = Column(String(200), nullable=False, index=True)
    
    # Team
    team_id = Column(Integer, nullable=True, index=True)
    team_key = Column(String(50), nullable=True, index=True)
    
    # Time range
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    period = Column(String(20), nullable=False)  # 'day', 'week', 'month'
    
    # Aggregated data (JSON arrays)
    dates = Column(JSON, nullable=False)  # List of dates in range
    importance_values = Column(JSON, nullable=False)  # List of importance scores
    sentiment_values = Column(JSON, nullable=False)  # List of sentiment scores
    frequency_values = Column(JSON, nullable=False)  # List of frequencies
    
    # Summary statistics
    avg_importance = Column(Float, nullable=False)
    max_importance = Column(Float, nullable=False)
    trend = Column(String(20), nullable=False)  # 'rising', 'falling', 'stable', 'emerging'
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_team_period', 'team_id', 'period', 'start_date'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'keyword': self.keyword,
            'team_key': self.team_key,
            'period': {
                'start': self.start_date.isoformat(),
                'end': self.end_date.isoformat(),
                'granularity': self.period,
            },
            'timeseries': {
                'dates': self.dates,
                'importance': self.importance_values,
                'sentiment': self.sentiment_values,
                'frequency': self.frequency_values,
            },
            'summary': {
                'avg_importance': round(self.avg_importance, 2),
                'max_importance': round(self.max_importance, 2),
                'trend': self.trend,
            }
        }
