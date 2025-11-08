"""
Repository for keyword importance and time-series data.
"""

from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, func, and_, desc
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

from keywords.importance_models import (
    KeywordImportanceModel,
    KeywordTimeSeriesModel,
    KeywordBase
)


def get_database_url(db_name: str = "keywords.db") -> str:
    """Get database URL for keywords database."""
    db_path = Path(__file__).parent.parent / "data" / db_name
    return f"sqlite:///{db_path}"


class ImportanceRepository:
    """Repository for keyword importance operations."""
    
    def __init__(self, db_url: Optional[str] = None):
        """Initialize repository."""
        self.db_url = db_url or get_database_url()
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        KeywordBase.metadata.create_all(self.engine)
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def save_importance(
        self,
        keyword: str,
        analysis_date: date,
        team_key: Optional[str],
        importance_score: float,
        frequency: int,
        document_count: int,
        source_diversity: int,
        velocity: float,
        acceleration: float,
        sentiment_score: float,
        sentiment_magnitude: float,
        positive_mentions: int,
        negative_mentions: int,
        neutral_mentions: int,
        content_ids: List[int],
        sample_snippets: List[Dict],
        team_id: Optional[int] = None,
        source_type: Optional[str] = None,
        source_name: Optional[str] = None,
        extraction_method: Optional[str] = None
    ) -> KeywordImportanceModel:
        """
        Save keyword importance record.
        
        Returns:
            Created/updated importance model
        """
        session = self._get_session()
        try:
            # Check if record exists for this keyword/date/team
            existing = session.query(KeywordImportanceModel).filter(
                and_(
                    KeywordImportanceModel.keyword == keyword,
                    KeywordImportanceModel.date == analysis_date,
                    KeywordImportanceModel.team_key == team_key
                )
            ).first()
            
            if existing:
                # Update existing record
                existing.importance_score = importance_score
                existing.frequency = frequency
                existing.document_count = document_count
                existing.source_diversity = source_diversity
                existing.velocity = velocity
                existing.acceleration = acceleration
                existing.sentiment_score = sentiment_score
                existing.sentiment_magnitude = sentiment_magnitude
                existing.positive_mentions = positive_mentions
                existing.negative_mentions = negative_mentions
                existing.neutral_mentions = neutral_mentions
                existing.content_ids = content_ids
                existing.sample_snippets = sample_snippets
                existing.updated_at = datetime.utcnow()
                
                record = existing
            else:
                # Create new record
                record = KeywordImportanceModel(
                    keyword=keyword,
                    keyword_normalized=keyword.lower(),
                    date=analysis_date,
                    team_id=team_id,
                    team_key=team_key,
                    source_type=source_type,
                    source_name=source_name,
                    frequency=frequency,
                    document_count=document_count,
                    source_diversity=source_diversity,
                    velocity=velocity,
                    acceleration=acceleration,
                    importance_score=importance_score,
                    sentiment_score=sentiment_score,
                    sentiment_magnitude=sentiment_magnitude,
                    positive_mentions=positive_mentions,
                    negative_mentions=negative_mentions,
                    neutral_mentions=neutral_mentions,
                    content_ids=content_ids,
                    sample_snippets=sample_snippets,
                    extraction_method=extraction_method,
                )
                session.add(record)
            
            session.commit()
            session.refresh(record)
            return record
        
        finally:
            session.close()
    
    def get_top_keywords(
        self,
        team_key: Optional[str],
        analysis_date: date,
        limit: int = 50,
        min_importance: float = 0.0
    ) -> List[KeywordImportanceModel]:
        """
        Get top keywords by importance for a team and date.
        
        Args:
            team_key: Team key (None for all teams)
            analysis_date: Date to get keywords for
            limit: Maximum number of keywords
            min_importance: Minimum importance threshold
        
        Returns:
            List of keyword importance records
        """
        session = self._get_session()
        try:
            query = session.query(KeywordImportanceModel).filter(
                and_(
                    KeywordImportanceModel.date == analysis_date,
                    KeywordImportanceModel.importance_score >= min_importance
                )
            )
            
            if team_key:
                query = query.filter(KeywordImportanceModel.team_key == team_key)
            
            query = query.order_by(desc(KeywordImportanceModel.importance_score))
            query = query.limit(limit)
            
            return query.all()
        
        finally:
            session.close()
    
    def get_keyword_history(
        self,
        keyword: str,
        team_key: Optional[str],
        start_date: date,
        end_date: date
    ) -> List[KeywordImportanceModel]:
        """
        Get historical importance data for a keyword.
        
        Args:
            keyword: Keyword to look up
            team_key: Team key
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            List of importance records over time
        """
        session = self._get_session()
        try:
            query = session.query(KeywordImportanceModel).filter(
                and_(
                    KeywordImportanceModel.keyword == keyword,
                    KeywordImportanceModel.date >= start_date,
                    KeywordImportanceModel.date <= end_date
                )
            )
            
            if team_key:
                query = query.filter(KeywordImportanceModel.team_key == team_key)
            
            query = query.order_by(KeywordImportanceModel.date)
            
            return query.all()
        
        finally:
            session.close()
    
    def save_timeseries(
        self,
        keyword: str,
        team_key: str,
        start_date: date,
        end_date: date,
        period: str,
        dates: List[str],
        importance_values: List[float],
        sentiment_values: List[float],
        frequency_values: List[int],
        avg_importance: float,
        max_importance: float,
        trend: str,
        team_id: Optional[int] = None
    ) -> KeywordTimeSeriesModel:
        """Save pre-computed time-series data."""
        session = self._get_session()
        try:
            # Check if exists
            existing = session.query(KeywordTimeSeriesModel).filter(
                and_(
                    KeywordTimeSeriesModel.keyword == keyword,
                    KeywordTimeSeriesModel.team_key == team_key,
                    KeywordTimeSeriesModel.start_date == start_date,
                    KeywordTimeSeriesModel.end_date == end_date,
                    KeywordTimeSeriesModel.period == period
                )
            ).first()
            
            if existing:
                # Update
                existing.dates = dates
                existing.importance_values = importance_values
                existing.sentiment_values = sentiment_values
                existing.frequency_values = frequency_values
                existing.avg_importance = avg_importance
                existing.max_importance = max_importance
                existing.trend = trend
                existing.updated_at = datetime.utcnow()
                record = existing
            else:
                # Create
                record = KeywordTimeSeriesModel(
                    keyword=keyword,
                    team_id=team_id,
                    team_key=team_key,
                    start_date=start_date,
                    end_date=end_date,
                    period=period,
                    dates=dates,
                    importance_values=importance_values,
                    sentiment_values=sentiment_values,
                    frequency_values=frequency_values,
                    avg_importance=avg_importance,
                    max_importance=max_importance,
                    trend=trend,
                )
                session.add(record)
            
            session.commit()
            session.refresh(record)
            return record
        
        finally:
            session.close()
    
    def get_timeseries(
        self,
        keyword: str,
        team_key: str,
        period: str = 'day'
    ) -> Optional[KeywordTimeSeriesModel]:
        """Get most recent time-series for a keyword."""
        session = self._get_session()
        try:
            return session.query(KeywordTimeSeriesModel).filter(
                and_(
                    KeywordTimeSeriesModel.keyword == keyword,
                    KeywordTimeSeriesModel.team_key == team_key,
                    KeywordTimeSeriesModel.period == period
                )
            ).order_by(desc(KeywordTimeSeriesModel.updated_at)).first()
        
        finally:
            session.close()
    
    def compute_timeseries_from_importance(
        self,
        keyword: str,
        team_key: str,
        days: int = 30
    ) -> Optional[KeywordTimeSeriesModel]:
        """
        Compute and save time-series from importance records.
        
        Args:
            keyword: Keyword to compute for
            team_key: Team key
            days: Number of days to include
        
        Returns:
            Time-series model
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get historical data
        history = self.get_keyword_history(keyword, team_key, start_date, end_date)
        
        if not history:
            return None
        
        # Extract arrays
        dates = [record.date.isoformat() for record in history]
        importance_values = [record.importance_score for record in history]
        sentiment_values = [record.sentiment_score for record in history]
        frequency_values = [record.frequency for record in history]
        
        # Calculate statistics
        avg_importance = sum(importance_values) / len(importance_values)
        max_importance = max(importance_values)
        
        # Determine trend
        if len(importance_values) >= 3:
            recent_avg = sum(importance_values[-3:]) / 3
            older_avg = sum(importance_values[:3]) / 3
            
            if recent_avg > older_avg * 1.5:
                trend = 'rising'
            elif recent_avg < older_avg * 0.7:
                trend = 'falling'
            elif avg_importance < 30 and recent_avg > older_avg:
                trend = 'emerging'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Save time-series
        return self.save_timeseries(
            keyword=keyword,
            team_key=team_key,
            start_date=start_date,
            end_date=end_date,
            period='day',
            dates=dates,
            importance_values=importance_values,
            sentiment_values=sentiment_values,
            frequency_values=frequency_values,
            avg_importance=avg_importance,
            max_importance=max_importance,
            trend=trend
        )
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()
