"""
Storage models and database setup for the sourcer pipeline.

This module handles persistent storage of sourced content with:
- Deduplication (content hashing)
- Metadata tracking (source type, timestamps, etc.)
- Efficient querying for downstream processing (NLP, sentiment analysis, etc.)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    Boolean,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib

Base = declarative_base()


class SourcedContentModel(Base):
    """
    Database model for sourced content.
    
    Designed for efficient storage and retrieval for NLP/ML processing:
    - Content hashing for deduplication
    - Full metadata for traceability
    - Indexed fields for fast querying
    - JSON fields for flexible metadata
    """

    __tablename__ = "sourced_content"

    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # Content fields
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(2048), nullable=True, index=True)
    
    # Metadata fields
    source_type = Column(String(50), nullable=False, index=True)  # 'rss', 'web', 'api', etc.
    source_name = Column(String(200), nullable=False, index=True)  # 'TechCrunch', 'HN', etc.
    source_url = Column(String(2048), nullable=False)  # Original feed/API URL
    
    # Authorship & dates
    author = Column(String(200), nullable=True)
    published_date = Column(DateTime, nullable=True, index=True)
    retrieved_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Additional metadata (flexible JSON field) - renamed to avoid SQLAlchemy conflict
    extra_metadata = Column(JSON, nullable=True)
    
    # Processing flags
    processed = Column(Boolean, default=False, nullable=False, index=True)
    processing_status = Column(String(50), nullable=True)  # 'pending', 'processing', 'completed', 'failed'
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_date', 'source_type', 'published_date'),
        Index('idx_processing', 'processed', 'processing_status'),
        Index('idx_retrieval_date', 'retrieved_at'),
    )

    def __repr__(self):
        return f"<SourcedContentModel(id={self.id}, title='{self.title[:30]}...', source={self.source_type})>"


class SourceConfigModel(Base):
    """
    Database model for source configurations.
    
    Tracks which sources to monitor and their fetch schedules.
    """

    __tablename__ = "source_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Source identification
    source_type = Column(String(50), nullable=False)  # 'rss', 'web', 'api'
    source_name = Column(String(200), nullable=False)
    source_url = Column(String(2048), nullable=False)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Source-specific config (max_entries, selectors, etc.)
    
    # Scheduling
    enabled = Column(Boolean, default=True, nullable=False)
    fetch_interval_minutes = Column(Integer, default=60, nullable=False)  # How often to fetch
    last_fetched_at = Column(DateTime, nullable=True)
    next_fetch_at = Column(DateTime, nullable=True)
    
    # Statistics
    total_items_fetched = Column(Integer, default=0, nullable=False)
    last_fetch_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('source_type', 'source_url', name='uq_source'),
        Index('idx_next_fetch', 'enabled', 'next_fetch_at'),
    )

    def __repr__(self):
        return f"<SourceConfigModel(name='{self.source_name}', type={self.source_type})>"


class ProcessingJobModel(Base):
    """
    Database model for tracking processing jobs (TF-IDF, sentiment, entities, etc.).
    
    Tracks batch processing operations on the content.
    """

    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Job identification
    job_type = Column(String(50), nullable=False, index=True)  # 'tfidf', 'sentiment', 'entities'
    job_name = Column(String(200), nullable=False)
    
    # Processing details
    content_filter = Column(JSON, nullable=True)  # Filters applied (date range, source type, etc.)
    items_processed = Column(Integer, default=0, nullable=False)
    items_total = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='pending', index=True)  # 'pending', 'running', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)  # Store processing results
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProcessingJobModel(id={self.id}, type={self.job_type}, status={self.status})>"


# Database setup utilities

def get_database_url(db_path: str = "data/sourcer_pipeline.db") -> str:
    """Get SQLite database URL."""
    return f"sqlite:///{db_path}"


def create_database(db_url: str = None):
    """
    Create database and all tables.
    
    Args:
        db_url: Database URL (defaults to SQLite)
    """
    if db_url is None:
        db_url = get_database_url()
    
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(db_url: str = None):
    """
    Get a database session.
    
    Args:
        db_url: Database URL (defaults to SQLite)
    
    Returns:
        SQLAlchemy session
    """
    if db_url is None:
        db_url = get_database_url()
    
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def compute_content_hash(content: str, url: str = None) -> str:
    """
    Compute a hash for content deduplication.
    
    Uses both content and URL to create a unique identifier.
    
    Args:
        content: Content text
        url: Content URL (optional)
    
    Returns:
        SHA-256 hash as hex string
    """
    # Normalize content (remove extra whitespace)
    normalized_content = " ".join(content.split())
    
    # Create hash from content + URL
    hash_input = normalized_content
    if url:
        hash_input += f"|{url}"
    
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
