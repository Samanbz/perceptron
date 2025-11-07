"""
Repository layer for database operations.

Provides high-level interface for storing and retrieving content with:
- Automatic deduplication
- Efficient querying
- Batch operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from .models import (
    SourcedContentModel,
    SourceConfigModel,
    compute_content_hash,
    get_session,
)
from sourcers.base import SourcedContent


class ContentRepository:
    """Repository for managing sourced content in the database."""

    def __init__(self, session: Session = None):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy session (will create one if not provided)
        """
        self.session = session or get_session()

    def save_content(
        self,
        content: SourcedContent,
        source_type: str,
        source_name: str,
        source_url: str,
    ) -> tuple[SourcedContentModel, bool]:
        """
        Save sourced content to database with deduplication.
        
        Args:
            content: SourcedContent object
            source_type: Type of source ('rss', 'web', 'api', etc.)
            source_name: Name of the source (e.g., 'TechCrunch')
            source_url: Original source URL (feed URL, API endpoint, etc.)
        
        Returns:
            Tuple of (SourcedContentModel, is_new)
            is_new is True if this is new content, False if duplicate
        """
        # Compute content hash for deduplication
        content_hash = compute_content_hash(content.content, content.url)
        
        # Check if content already exists
        existing = self.session.query(SourcedContentModel).filter(
            SourcedContentModel.content_hash == content_hash
        ).first()
        
        if existing:
            return existing, False
        
        # Create new content record
        db_content = SourcedContentModel(
            content_hash=content_hash,
            title=content.title,
            content=content.content,
            url=content.url,
            source_type=source_type,
            source_name=source_name,
            source_url=source_url,
            author=content.author,
            published_date=content.published_date,
            retrieved_at=content.retrieved_at,
            extra_metadata=content.metadata,
            processed=False,
            processing_status='pending',
        )
        
        self.session.add(db_content)
        self.session.commit()
        
        return db_content, True

    def save_batch(
        self,
        contents: List[SourcedContent],
        source_type: str,
        source_name: str,
        source_url: str,
    ) -> Dict[str, int]:
        """
        Save multiple contents efficiently.
        
        Args:
            contents: List of SourcedContent objects
            source_type: Type of source
            source_name: Name of the source
            source_url: Original source URL
        
        Returns:
            Dict with statistics: {'saved': int, 'duplicates': int, 'total': int}
        """
        saved = 0
        duplicates = 0
        
        for content in contents:
            _, is_new = self.save_content(content, source_type, source_name, source_url)
            if is_new:
                saved += 1
            else:
                duplicates += 1
        
        return {
            'saved': saved,
            'duplicates': duplicates,
            'total': len(contents),
        }

    def get_unprocessed_content(
        self,
        limit: int = 100,
        source_type: str = None,
    ) -> List[SourcedContentModel]:
        """
        Get content that hasn't been processed yet.
        
        Args:
            limit: Maximum number of items to return
            source_type: Filter by source type (optional)
        
        Returns:
            List of unprocessed content
        """
        query = self.session.query(SourcedContentModel).filter(
            SourcedContentModel.processed == False
        )
        
        if source_type:
            query = query.filter(SourcedContentModel.source_type == source_type)
        
        return query.order_by(SourcedContentModel.published_date.desc()).limit(limit).all()

    def get_content_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime = None,
        source_type: str = None,
    ) -> List[SourcedContentModel]:
        """
        Get content within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive), defaults to now
            source_type: Filter by source type (optional)
        
        Returns:
            List of content within date range
        """
        if end_date is None:
            end_date = datetime.now()
        
        query = self.session.query(SourcedContentModel).filter(
            and_(
                SourcedContentModel.published_date >= start_date,
                SourcedContentModel.published_date <= end_date,
            )
        )
        
        if source_type:
            query = query.filter(SourcedContentModel.source_type == source_type)
        
        return query.order_by(desc(SourcedContentModel.published_date)).all()

    def mark_as_processed(
        self,
        content_id: int,
        status: str = 'completed',
    ):
        """
        Mark content as processed.
        
        Args:
            content_id: Content ID
            status: Processing status ('completed', 'failed', etc.)
        """
        content = self.session.query(SourcedContentModel).get(content_id)
        if content:
            content.processed = True
            content.processing_status = status
            self.session.commit()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics about stored content
        """
        total_content = self.session.query(SourcedContentModel).count()
        processed = self.session.query(SourcedContentModel).filter(
            SourcedContentModel.processed == True
        ).count()
        
        # Count by source type
        from sqlalchemy import func
        by_source_type = {}
        results = self.session.query(
            SourcedContentModel.source_type,
            func.count(SourcedContentModel.id)
        ).group_by(SourcedContentModel.source_type).all()
        
        for source_type, count in results:
            by_source_type[source_type] = count
        
        return {
            'total_content': total_content,
            'processed': processed,
            'unprocessed': total_content - processed,
            'by_source_type': by_source_type,
        }

    def close(self):
        """Close database session."""
        self.session.close()


class SourceConfigRepository:
    """Repository for managing source configurations."""

    def __init__(self, session: Session = None):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy session (will create one if not provided)
        """
        self.session = session or get_session()

    def add_source(
        self,
        source_type: str,
        source_name: str,
        source_url: str,
        config: Dict[str, Any] = None,
        fetch_interval_minutes: int = 60,
    ) -> SourceConfigModel:
        """
        Add a new source to monitor.
        
        Args:
            source_type: Type of source ('rss', 'web', etc.)
            source_name: Name of the source
            source_url: Source URL
            config: Source-specific configuration
            fetch_interval_minutes: How often to fetch (in minutes)
        
        Returns:
            Created SourceConfigModel
        """
        # Check if source already exists
        existing = self.session.query(SourceConfigModel).filter(
            and_(
                SourceConfigModel.source_type == source_type,
                SourceConfigModel.source_url == source_url,
            )
        ).first()
        
        if existing:
            return existing
        
        # Calculate next fetch time
        next_fetch = datetime.now() + timedelta(minutes=fetch_interval_minutes)
        
        source_config = SourceConfigModel(
            source_type=source_type,
            source_name=source_name,
            source_url=source_url,
            config=config or {},
            fetch_interval_minutes=fetch_interval_minutes,
            next_fetch_at=next_fetch,
            enabled=True,
        )
        
        self.session.add(source_config)
        self.session.commit()
        
        return source_config

    def get_sources_to_fetch(self) -> List[SourceConfigModel]:
        """
        Get sources that are due for fetching.
        
        Returns:
            List of source configurations ready to fetch
        """
        now = datetime.now()
        
        return self.session.query(SourceConfigModel).filter(
            and_(
                SourceConfigModel.enabled == True,
                or_(
                    SourceConfigModel.next_fetch_at <= now,
                    SourceConfigModel.next_fetch_at == None,
                )
            )
        ).all()

    def update_fetch_status(
        self,
        source_id: int,
        items_fetched: int,
        error: str = None,
    ):
        """
        Update source fetch status.
        
        Args:
            source_id: Source configuration ID
            items_fetched: Number of items fetched
            error: Error message if fetch failed
        """
        source = self.session.query(SourceConfigModel).get(source_id)
        if source:
            source.last_fetched_at = datetime.now()
            source.last_fetch_count = items_fetched
            source.total_items_fetched += items_fetched
            source.next_fetch_at = datetime.now() + timedelta(minutes=source.fetch_interval_minutes)
            
            if error:
                source.last_error = error
            else:
                source.last_error = None
            
            self.session.commit()

    def list_sources(self, enabled_only: bool = False) -> List[SourceConfigModel]:
        """
        List all source configurations.
        
        Args:
            enabled_only: If True, only return enabled sources
        
        Returns:
            List of source configurations
        """
        query = self.session.query(SourceConfigModel)
        
        if enabled_only:
            query = query.filter(SourceConfigModel.enabled == True)
        
        return query.all()

    def disable_source(self, source_id: int):
        """Disable a source."""
        source = self.session.query(SourceConfigModel).get(source_id)
        if source:
            source.enabled = False
            self.session.commit()

    def enable_source(self, source_id: int):
        """Enable a source."""
        source = self.session.query(SourceConfigModel).get(source_id)
        if source:
            source.enabled = True
            self.session.commit()

    def close(self):
        """Close database session."""
        self.session.close()
