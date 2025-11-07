"""
Real-time keyword extraction processor.

Processes content as it arrives in the data lake and extracts keywords immediately.
"""

import time
from datetime import date
from typing import Optional
import logging

from .extractor import KeywordExtractor
from .repository import KeywordRepository, KeywordConfigRepository


logger = logging.getLogger(__name__)


class RealtimeKeywordProcessor:
    """
    Real-time keyword extraction processor.
    
    Extracts keywords from content immediately after ingestion.
    Uses active configuration for extraction parameters.
    """

    def __init__(
        self,
        extractor: Optional[KeywordExtractor] = None,
        keyword_repo: Optional[KeywordRepository] = None,
        config_repo: Optional[KeywordConfigRepository] = None,
    ):
        """
        Initialize processor.
        
        Args:
            extractor: KeywordExtractor instance (will create if not provided)
            keyword_repo: KeywordRepository instance (will create if not provided)
            config_repo: KeywordConfigRepository instance (will create if not provided)
        """
        self.extractor = extractor or KeywordExtractor()
        self.keyword_repo = keyword_repo or KeywordRepository()
        self.config_repo = config_repo or KeywordConfigRepository()

    def process_content(
        self,
        content_id: int,
        title: str,
        content: str,
        source_type: str,
        source_name: str,
        extraction_date: Optional[date] = None,
    ) -> dict:
        """
        Process a single piece of content and extract keywords.
        
        Args:
            content_id: Content ID from data lake
            title: Content title
            content: Content text
            source_type: Source type ('rss', etc.)
            source_name: Source name ('TechCrunch', etc.)
            extraction_date: Date for keyword association (defaults to today)
        
        Returns:
            Processing result with statistics
        """
        start_time = time.time()
        
        try:
            # Get active config
            config = self.config_repo.get_active_config()
            if not config:
                logger.warning("No active configuration found, using defaults")
                config_name = "default"
                relevance_threshold = 0.7
                tfidf_weight = 0.3
                spacy_weight = 0.4
                yake_weight = 0.3
                max_keywords = 50
            else:
                config_name = config.config_name
                relevance_threshold = config.relevance_threshold
                tfidf_weight = config.tfidf_weight
                spacy_weight = config.spacy_weight
                yake_weight = config.yake_weight
                max_keywords = config.max_keywords_per_source
            
            # Extract keywords
            logger.info(f"Extracting keywords from content {content_id}: {title[:50]}...")
            
            keywords = self.extractor.extract(
                text=content,
                title=title,
                max_keywords=max_keywords,
                tfidf_weight=tfidf_weight,
                spacy_weight=spacy_weight,
                yake_weight=yake_weight,
            )
            
            keywords_extracted = len(keywords)
            
            # Save keywords with threshold filtering
            if extraction_date is None:
                extraction_date = date.today()
            
            keywords_stored = self.keyword_repo.save_keywords(
                keywords=keywords,
                content_id=content_id,
                extraction_date=extraction_date,
                source_type=source_type,
                source_name=source_name,
                relevance_threshold=relevance_threshold,
            )
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Log the extraction
            self.keyword_repo.log_extraction(
                content_id=content_id,
                content_title=title,
                keywords_extracted=keywords_extracted,
                keywords_stored=keywords_stored,
                config_name=config_name,
                relevance_threshold=relevance_threshold,
                processing_time_ms=processing_time_ms,
                status='success',
            )
            
            logger.info(
                f"Processed content {content_id}: "
                f"{keywords_extracted} keywords extracted, "
                f"{keywords_stored} stored (threshold={relevance_threshold:.2f}), "
                f"{processing_time_ms:.1f}ms"
            )
            
            return {
                'status': 'success',
                'content_id': content_id,
                'keywords_extracted': keywords_extracted,
                'keywords_stored': keywords_stored,
                'relevance_threshold': relevance_threshold,
                'processing_time_ms': processing_time_ms,
            }
        
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            error_message = str(e)
            
            logger.error(f"Failed to process content {content_id}: {error_message}")
            
            # Log the failure
            self.keyword_repo.log_extraction(
                content_id=content_id,
                content_title=title,
                keywords_extracted=0,
                keywords_stored=0,
                config_name=config_name if 'config_name' in locals() else 'unknown',
                relevance_threshold=relevance_threshold if 'relevance_threshold' in locals() else 0.0,
                processing_time_ms=processing_time_ms,
                status='failed',
                error_message=error_message,
            )
            
            return {
                'status': 'failed',
                'content_id': content_id,
                'error': error_message,
                'processing_time_ms': processing_time_ms,
            }

    def process_batch(self, content_items: list) -> dict:
        """
        Process a batch of content items.
        
        Args:
            content_items: List of dicts with content data
                Expected keys: id, title, content, source_type, source_name
        
        Returns:
            Batch processing results
        """
        results = {
            'total': len(content_items),
            'successful': 0,
            'failed': 0,
            'keywords_extracted': 0,
            'keywords_stored': 0,
            'processing_time_ms': 0,
        }
        
        for item in content_items:
            result = self.process_content(
                content_id=item['id'],
                title=item['title'],
                content=item['content'],
                source_type=item['source_type'],
                source_name=item['source_name'],
                extraction_date=item.get('extraction_date'),
            )
            
            if result['status'] == 'success':
                results['successful'] += 1
                results['keywords_extracted'] += result['keywords_extracted']
                results['keywords_stored'] += result['keywords_stored']
            else:
                results['failed'] += 1
            
            results['processing_time_ms'] += result['processing_time_ms']
        
        return results

    def close(self):
        """Clean up resources."""
        self.keyword_repo.close()
        self.config_repo.close()
