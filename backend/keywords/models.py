"""
Database models for keyword extraction and storage.

Stores extracted keywords with relevance scores and metadata.
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
    Index,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

# Reuse the Base from storage.models if needed, or create separate
KeywordBase = declarative_base()


class ExtractedKeywordModel(KeywordBase):
    """
    Stores extracted keywords with relevance scores.
    
    Designed for:
    - Real-time keyword extraction
    - Dynamic relevance thresholding
    - Aggregation by date/source
    - Fast querying for dashboards
    """

    __tablename__ = "extracted_keywords"

    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Keyword information
    keyword = Column(String(200), nullable=False, index=True)
    keyword_type = Column(String(50), nullable=False)  # 'single', 'phrase', 'entity'
    entity_type = Column(String(50), nullable=True)    # 'PERSON', 'ORG', 'GPE', 'PRODUCT', etc.
    
    # Relevance scores
    relevance_score = Column(Float, nullable=False, index=True)  # Combined score 0-1
    tfidf_score = Column(Float, nullable=True)
    spacy_score = Column(Float, nullable=True)
    yake_score = Column(Float, nullable=True)
    
    # Frequency
    frequency = Column(Integer, default=1, nullable=False)  # How many times appeared
    document_count = Column(Integer, default=1, nullable=False)  # In how many documents
    
    # Time information
    extraction_date = Column(Date, nullable=False, index=True)
    first_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Source information
    source_type = Column(String(50), nullable=False, index=True)
    source_name = Column(String(200), nullable=False, index=True)
    
    # Content references
    content_ids = Column(JSON, nullable=True)  # List of content IDs containing this keyword
    sample_context = Column(Text, nullable=True)  # Sample sentence showing keyword in context
    
    # Metadata
    extraction_method = Column(String(100), nullable=True)  # 'tfidf+spacy+yake'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite indexes for common queries
    __table_args__ = (
        # Unique constraint: one keyword per day per source
        UniqueConstraint('keyword', 'extraction_date', 'source_type', 'source_name', 
                        name='uq_keyword_date_source'),
        # Index for high-relevance queries
        Index('idx_relevance_date', 'relevance_score', 'extraction_date'),
        # Index for source queries
        Index('idx_source_date', 'source_type', 'source_name', 'extraction_date'),
    )

    def __repr__(self):
        return f"<ExtractedKeyword(keyword='{self.keyword}', score={self.relevance_score:.2f}, date={self.extraction_date})>"


class KeywordExtractionConfigModel(KeywordBase):
    """
    Configuration for keyword extraction parameters.
    
    Allows dynamic tuning of extraction parameters.
    """

    __tablename__ = "keyword_extraction_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Configuration name
    config_name = Column(String(100), nullable=False, unique=True)
    
    # Threshold settings
    relevance_threshold = Column(Float, default=0.7, nullable=False)  # Minimum relevance score
    min_frequency = Column(Integer, default=1, nullable=False)  # Minimum mentions
    min_document_count = Column(Integer, default=1, nullable=False)  # Minimum documents
    
    # Extraction settings
    max_keywords_per_source = Column(Integer, default=50, nullable=False)
    max_phrase_length = Column(Integer, default=2, nullable=False)  # Max words in phrase
    min_phrase_length = Column(Integer, default=1, nullable=False)  # Min words in phrase
    
    # Method weights (for combining scores)
    tfidf_weight = Column(Float, default=0.3, nullable=False)
    spacy_weight = Column(Float, default=0.4, nullable=False)
    yake_weight = Column(Float, default=0.3, nullable=False)
    
    # Active flag
    is_active = Column(Integer, default=0, nullable=False)  # 1 = active config
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<KeywordConfig(name='{self.config_name}', threshold={self.relevance_threshold})>"


class KeywordExtractionLogModel(KeywordBase):
    """
    Logs each keyword extraction run for monitoring.
    """

    __tablename__ = "keyword_extraction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Content processed
    content_id = Column(Integer, nullable=False, index=True)
    content_title = Column(String(500), nullable=True)
    
    # Extraction results
    keywords_extracted = Column(Integer, default=0, nullable=False)
    keywords_stored = Column(Integer, default=0, nullable=False)  # After threshold filtering
    
    # Configuration used
    config_name = Column(String(100), nullable=True)
    relevance_threshold = Column(Float, nullable=True)
    
    # Performance
    processing_time_ms = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='success')  # 'success', 'failed', 'partial'
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_content_date', 'content_id', 'created_at'),
    )

    def __repr__(self):
        return f"<KeywordLog(content_id={self.content_id}, extracted={self.keywords_extracted})>"


# Database setup utilities for keywords

def get_keyword_database_url(db_path: str = "data/keywords.db") -> str:
    """Get SQLite database URL for keywords."""
    return f"sqlite:///{db_path}"


def create_keyword_database(db_url: str = None):
    """
    Create keyword database and all tables.
    
    Args:
        db_url: Database URL (defaults to SQLite)
    """
    from sqlalchemy import create_engine
    
    if db_url is None:
        db_url = get_keyword_database_url()
    
    engine = create_engine(db_url, echo=False)
    KeywordBase.metadata.create_all(engine)
    return engine


def get_keyword_session(db_url: str = None):
    """
    Get a database session for keywords.
    
    Args:
        db_url: Database URL (defaults to SQLite)
    
    Returns:
        SQLAlchemy session
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    if db_url is None:
        db_url = get_keyword_database_url()
    
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def create_keyword_tables(db_url: Optional[str] = None):
    """
    Create all keyword database tables.
    
    Args:
        db_url: Database URL (defaults to keywords.db)
    """
    from sqlalchemy import create_engine
    
    if db_url is None:
        db_url = get_keyword_database_url()
    
    engine = create_engine(db_url, echo=False)
    KeywordBase.metadata.create_all(engine)
