"""
Repository layer for keyword storage and retrieval.
"""

from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from .models import (
    ExtractedKeywordModel,
    KeywordExtractionConfigModel,
    KeywordExtractionLogModel,
    get_keyword_session,
)


class KeywordRepository:
    """Repository for managing extracted keywords."""

    def __init__(self, session: Session = None):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy session (will create one if not provided)
        """
        self.session = session or get_keyword_session()

    def save_keywords(
        self,
        keywords: List[Dict],
        content_id: int,
        extraction_date: date,
        source_type: str,
        source_name: str,
        relevance_threshold: float = 0.0,
    ) -> int:
        """
        Save extracted keywords to database.
        
        Args:
            keywords: List of keyword dicts from extractor
            content_id: Source content ID
            extraction_date: Date to associate with keywords
            source_type: Source type ('rss', etc.)
            source_name: Source name ('TechCrunch', etc.)
            relevance_threshold: Minimum relevance score to save
        
        Returns:
            Number of keywords saved
        """
        saved_count = 0
        
        for kw_data in keywords:
            # Check threshold
            if kw_data['relevance_score'] < relevance_threshold:
                continue
            
            # Check if keyword already exists for this date/source
            existing = self.session.query(ExtractedKeywordModel).filter(
                and_(
                    ExtractedKeywordModel.keyword == kw_data['keyword'],
                    ExtractedKeywordModel.extraction_date == extraction_date,
                    ExtractedKeywordModel.source_type == source_type,
                    ExtractedKeywordModel.source_name == source_name,
                )
            ).first()
            
            if existing:
                # Update existing keyword
                existing.frequency += 1
                existing.document_count += 1
                existing.last_seen = datetime.utcnow()
                
                # Update scores (take max)
                existing.relevance_score = max(existing.relevance_score, kw_data['relevance_score'])
                existing.tfidf_score = max(existing.tfidf_score or 0, kw_data.get('tfidf_score', 0))
                existing.spacy_score = max(existing.spacy_score or 0, kw_data.get('spacy_score', 0))
                existing.yake_score = max(existing.yake_score or 0, kw_data.get('yake_score', 0))
                
                # Add content ID to list
                if existing.content_ids is None:
                    existing.content_ids = []
                if content_id not in existing.content_ids:
                    existing.content_ids.append(content_id)
            else:
                # Create new keyword
                keyword = ExtractedKeywordModel(
                    keyword=kw_data['keyword'],
                    keyword_type=kw_data['type'],
                    entity_type=kw_data.get('entity_type'),
                    relevance_score=kw_data['relevance_score'],
                    tfidf_score=kw_data.get('tfidf_score'),
                    spacy_score=kw_data.get('spacy_score'),
                    yake_score=kw_data.get('yake_score'),
                    frequency=1,
                    document_count=1,
                    extraction_date=extraction_date,
                    source_type=source_type,
                    source_name=source_name,
                    content_ids=[content_id],
                    extraction_method='tfidf+spacy+yake',
                )
                self.session.add(keyword)
            
            saved_count += 1
        
        self.session.commit()
        return saved_count

    def get_daily_keywords(
        self,
        extraction_date: date,
        source_type: Optional[str] = None,
        source_name: Optional[str] = None,
        min_relevance: float = 0.0,
        limit: int = 100,
    ) -> List[ExtractedKeywordModel]:
        """
        Get keywords for a specific date.
        
        Args:
            extraction_date: Date to query
            source_type: Filter by source type (optional)
            source_name: Filter by source name (optional)
            min_relevance: Minimum relevance score
            limit: Maximum results
        
        Returns:
            List of keyword models
        """
        query = self.session.query(ExtractedKeywordModel).filter(
            and_(
                ExtractedKeywordModel.extraction_date == extraction_date,
                ExtractedKeywordModel.relevance_score >= min_relevance,
            )
        )
        
        if source_type:
            query = query.filter(ExtractedKeywordModel.source_type == source_type)
        
        if source_name:
            query = query.filter(ExtractedKeywordModel.source_name == source_name)
        
        return query.order_by(desc(ExtractedKeywordModel.relevance_score)).limit(limit).all()

    def get_top_keywords(
        self,
        days: int = 7,
        source_type: Optional[str] = None,
        min_relevance: float = 0.7,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get top keywords aggregated over recent days.
        
        Args:
            days: Number of days to look back
            source_type: Filter by source type (optional)
            min_relevance: Minimum relevance score
            limit: Maximum results
        
        Returns:
            List of aggregated keyword data
        """
        start_date = date.today() - timedelta(days=days)
        
        query = self.session.query(
            ExtractedKeywordModel.keyword,
            func.max(ExtractedKeywordModel.relevance_score).label('max_score'),
            func.sum(ExtractedKeywordModel.frequency).label('total_frequency'),
            func.count(ExtractedKeywordModel.id).label('appearance_count'),
        ).filter(
            and_(
                ExtractedKeywordModel.extraction_date >= start_date,
                ExtractedKeywordModel.relevance_score >= min_relevance,
            )
        )
        
        if source_type:
            query = query.filter(ExtractedKeywordModel.source_type == source_type)
        
        query = query.group_by(ExtractedKeywordModel.keyword)
        query = query.order_by(desc('max_score'))
        query = query.limit(limit)
        
        results = []
        for row in query.all():
            results.append({
                'keyword': row.keyword,
                'max_relevance': float(row.max_score),
                'total_frequency': int(row.total_frequency),
                'appearance_count': int(row.appearance_count),
            })
        
        return results

    def log_extraction(
        self,
        content_id: int,
        content_title: str,
        keywords_extracted: int,
        keywords_stored: int,
        config_name: str,
        relevance_threshold: float,
        processing_time_ms: float,
        status: str = 'success',
        error_message: str = None,
    ):
        """
        Log a keyword extraction operation.
        
        Args:
            content_id: Content ID processed
            content_title: Content title
            keywords_extracted: Total keywords extracted
            keywords_stored: Keywords stored after filtering
            config_name: Configuration used
            relevance_threshold: Threshold applied
            processing_time_ms: Processing time in milliseconds
            status: Status ('success', 'failed', 'partial')
            error_message: Error message if failed
        """
        log = KeywordExtractionLogModel(
            content_id=content_id,
            content_title=content_title,
            keywords_extracted=keywords_extracted,
            keywords_stored=keywords_stored,
            config_name=config_name,
            relevance_threshold=relevance_threshold,
            processing_time_ms=processing_time_ms,
            status=status,
            error_message=error_message,
        )
        
        self.session.add(log)
        self.session.commit()

    def get_statistics(self) -> Dict:
        """
        Get keyword database statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_keywords = self.session.query(ExtractedKeywordModel).count()
        
        # Unique keywords
        unique_keywords = self.session.query(
            func.count(func.distinct(ExtractedKeywordModel.keyword))
        ).scalar()
        
        # By source
        by_source = {}
        results = self.session.query(
            ExtractedKeywordModel.source_name,
            func.count(ExtractedKeywordModel.id)
        ).group_by(ExtractedKeywordModel.source_name).all()
        
        for source_name, count in results:
            by_source[source_name] = count
        
        # Recent activity
        today = date.today()
        today_count = self.session.query(ExtractedKeywordModel).filter(
            ExtractedKeywordModel.extraction_date == today
        ).count()
        
        return {
            'total_keywords': total_keywords,
            'unique_keywords': unique_keywords,
            'by_source': by_source,
            'today': today_count,
        }

    def close(self):
        """Close database session."""
        self.session.close()


class KeywordConfigRepository:
    """Repository for managing keyword extraction configurations."""

    def __init__(self, session: Session = None):
        """Initialize repository."""
        self.session = session or get_keyword_session()

    def get_active_config(self) -> Optional[KeywordExtractionConfigModel]:
        """
        Get the active configuration.
        
        Returns:
            Active config or None
        """
        return self.session.query(KeywordExtractionConfigModel).filter(
            KeywordExtractionConfigModel.is_active == 1
        ).first()

    def set_active_config(self, config_name: str):
        """
        Set a configuration as active.
        
        Args:
            config_name: Name of config to activate
        """
        # Deactivate all
        self.session.query(KeywordExtractionConfigModel).update(
            {'is_active': 0}
        )
        
        # Activate the specified one
        config = self.session.query(KeywordExtractionConfigModel).filter(
            KeywordExtractionConfigModel.config_name == config_name
        ).first()
        
        if config:
            config.is_active = 1
            self.session.commit()

    def create_config(
        self,
        config_name: str,
        relevance_threshold: float = 0.7,
        **kwargs
    ) -> KeywordExtractionConfigModel:
        """
        Create a new configuration.
        
        Args:
            config_name: Unique name for config
            relevance_threshold: Minimum relevance score
            **kwargs: Additional config parameters
        
        Returns:
            Created config model
        """
        config = KeywordExtractionConfigModel(
            config_name=config_name,
            relevance_threshold=relevance_threshold,
            **kwargs
        )
        
        self.session.add(config)
        self.session.commit()
        
        return config

    def list_configs(self) -> List[KeywordExtractionConfigModel]:
        """List all configurations."""
        return self.session.query(KeywordExtractionConfigModel).all()

    def close(self):
        """Close database session."""
        self.session.close()
