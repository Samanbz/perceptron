"""
Enhanced real-time keyword processor with importance and sentiment analysis.

Complete NLP pipeline:
1. Extract keywords (TF-IDF + spaCy + YAKE)
2. Calculate importance (multi-signal algorithm)
3. Analyze sentiment (VADER + contextual)
4. Store structured data for frontend
"""

import time
from datetime import date, timedelta
from typing import Optional, List, Dict
from collections import defaultdict
import logging

from .extractor import KeywordExtractor
from .repository import KeywordRepository, KeywordConfigRepository
from .importance import ImportanceCalculator
from .sentiment import SentimentAnalyzer
from .importance_repository import ImportanceRepository
from storage.repository import ContentRepository


logger = logging.getLogger(__name__)


class EnhancedKeywordProcessor:
    """
    Enhanced real-time processor with full NLP pipeline.
    
    Pipeline:
    1. Content arrives from data lake
    2. Extract keywords using multi-method approach
    3. Calculate importance using state-of-the-art signals
    4. Analyze sentiment in context
    5. Store structured data ready for frontend API
    """
    
    def __init__(
        self,
        extractor: Optional[KeywordExtractor] = None,
        importance_calc: Optional[ImportanceCalculator] = None,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None,
        keyword_repo: Optional[KeywordRepository] = None,
        importance_repo: Optional[ImportanceRepository] = None,
        config_repo: Optional[KeywordConfigRepository] = None,
        content_repo: Optional[ContentRepository] = None,
        team_key: Optional[str] = None,
    ):
        """
        Initialize enhanced processor.
        
        Args:
            extractor: Keyword extractor
            importance_calc: Importance calculator
            sentiment_analyzer: Sentiment analyzer
            keyword_repo: Keyword repository
            importance_repo: Importance repository
            config_repo: Config repository
            content_repo: Content repository (data lake)
            team_key: Team to process for (filters sources)
        """
        self.extractor = extractor or KeywordExtractor()
        self.importance_calc = importance_calc or ImportanceCalculator()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
        self.keyword_repo = keyword_repo or KeywordRepository()
        self.importance_repo = importance_repo or ImportanceRepository()
        self.config_repo = config_repo or KeywordConfigRepository()
        self.content_repo = content_repo or ContentRepository()
        self.team_key = team_key
        
        # Cache for batch processing
        self.keyword_cache = defaultdict(lambda: {
            'frequency': 0,
            'documents': [],
            'snippets': [],
            'content_ids': [],
        })
    
    def process_content(
        self,
        content_id: int,
        title: str,
        content: str,
        source_type: str,
        source_name: str,
        published_date: Optional[date] = None,
        extraction_date: Optional[date] = None,
        team_key: Optional[str] = None,
    ) -> Dict:
        """
        Process a single piece of content through full NLP pipeline.
        
        Args:
            content_id: Content ID from data lake
            title: Content title
            content: Content text
            source_type: Source type
            source_name: Source name
            published_date: When content was published
            extraction_date: Date for keyword association
            team_key: Team context (overrides instance team_key)
        
        Returns:
            Processing results with statistics
        """
        start_time = time.time()
        team = team_key or self.team_key
        
        if extraction_date is None:
            extraction_date = date.today()
        
        try:
            # Step 1: Extract keywords
            logger.info(f"Extracting keywords from content {content_id}: {title[:50]}...")
            
            keywords = self.extractor.extract(
                text=content,
                title=title,
                max_keywords=100,
            )
            
            keywords_extracted = len(keywords)
            logger.info(f"Extracted {keywords_extracted} keywords")
            
            # Step 2: Store basic keywords
            keywords_stored = self.keyword_repo.save_keywords(
                keywords=keywords,
                content_id=content_id,
                extraction_date=extraction_date,
                source_type=source_type,
                source_name=source_name,
                relevance_threshold=0.3,  # Store more keywords, filter during importance calculation
            )
            
            # Step 3: Update cache for batch importance calculation
            for kw_data in keywords:
                kw = kw_data['keyword']
                score = kw_data['relevance_score']
                self.keyword_cache[kw]['frequency'] += 1
                self.keyword_cache[kw]['documents'].append({
                    'content_id': content_id,
                    'title': title,
                    'content': content,
                    'source_name': source_name,
                    'published_date': published_date,
                })
                self.keyword_cache[kw]['content_ids'].append(content_id)
                
                # Extract snippets containing keyword
                snippets = self.sentiment_analyzer.extract_keyword_context(
                    content + ' ' + title,
                    kw,
                    window=100
                )
                self.keyword_cache[kw]['snippets'].extend(snippets)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Processed content {content_id}: "
                f"{keywords_extracted} keywords extracted, "
                f"{keywords_stored} stored, "
                f"{processing_time_ms:.1f}ms"
            )
            
            return {
                'status': 'success',
                'content_id': content_id,
                'keywords_extracted': keywords_extracted,
                'keywords_stored': keywords_stored,
                'processing_time_ms': processing_time_ms,
            }
        
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed to process content {content_id}: {e}")
            
            return {
                'status': 'failed',
                'content_id': content_id,
                'error': str(e),
                'processing_time_ms': processing_time_ms,
            }
    
    def calculate_importance_and_sentiment(
        self,
        analysis_date: Optional[date] = None,
        team_key: Optional[str] = None,
        min_frequency: int = 1,  # Changed from 2 to capture single-occurrence important keywords
    ) -> Dict:
        """
        Calculate importance and sentiment for cached keywords.
        
        Should be called after processing a batch of content.
        
        Args:
            analysis_date: Date to associate with analysis
            team_key: Team context
            min_frequency: Minimum frequency to process
        
        Returns:
            Statistics about importance calculation
        """
        start_time = time.time()
        team = team_key or self.team_key
        
        if analysis_date is None:
            analysis_date = date.today()
        
        logger.info(f"Calculating importance for {len(self.keyword_cache)} keywords...")
        
        # Batch encode all keywords upfront for efficiency
        keywords_to_process = [
            kw for kw, data in self.keyword_cache.items()
            if data['frequency'] >= min_frequency
        ]
        
        logger.info(f"Batch encoding {len(keywords_to_process)} keywords...")
        keyword_embeddings = self.importance_calc.batch_encode_keywords(keywords_to_process)
        logger.info(f"Batch encoding complete")
        
        # Get data lake statistics once (shared across all keywords)
        try:
            data_lake_stats = self.content_repo.get_statistics()
            total_documents = data_lake_stats.get('total_content', 100)
            corpus_size = max(total_documents * 500, 1000)
        except Exception as e:
            logger.warning(f"Failed to get data lake stats, using defaults: {e}")
            total_documents = 100
            corpus_size = 10000
        
        keywords_processed = 0
        keywords_saved = 0
        
        # Prepare all keyword data for batch processing
        keyword_batch_data = []
        for keyword, data in self.keyword_cache.items():
            frequency = data['frequency']
            
            # Skip low-frequency keywords
            if frequency < min_frequency:
                continue
            
            # Get historical frequencies for velocity calculation
            history = self.importance_repo.get_keyword_history(
                keyword=keyword,
                team_key=team,
                start_date=analysis_date - timedelta(days=30),
                end_date=analysis_date - timedelta(days=1)
            )
            previous_frequencies = [h.frequency for h in history]
            
            # Count unique sources
            source_diversity = len(set(
                doc['source_name'] for doc in data['documents']
            ))
            
            keyword_batch_data.append({
                'keyword': keyword,
                'data': data,
                'frequency': frequency,
                'previous_frequencies': previous_frequencies,
                'source_diversity': source_diversity,
                'keyword_embedding': keyword_embeddings.get(keyword),
            })
        
        logger.info(f"Processing {len(keyword_batch_data)} keywords in optimized batches...")
        
        # Process in larger batches for better throughput
        import math
        import multiprocessing
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
        
        # Use CPU count for optimal parallelism
        num_workers = max(1, multiprocessing.cpu_count() - 1)
        batch_size = 50  # Smaller batches for better distribution
        
        logger.info(f"Using {num_workers} worker threads for parallel processing")
        
        try:
            # Use ThreadPoolExecutor with more workers (GIL is released during I/O and C extensions)
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                
                def process_keyword(kw_info):
                    keyword = kw_info['keyword']
                    data = kw_info['data']
                    
                    # Calculate sentiment
                    sentiment_result = self.sentiment_analyzer.analyze_keyword_sentiment(
                        keyword=keyword,
                        documents=data['documents'],
                        context_window=100
                    )
                    
                    # Calculate importance
                    importance_result = self.importance_calc.calculate_importance(
                        keyword=keyword,
                        frequency=kw_info['frequency'],
                        document_count=len(data['documents']),
                        source_diversity=kw_info['source_diversity'],
                        snippets=data['snippets'][:20],
                        previous_frequencies=kw_info['previous_frequencies'],
                        sentiment_score=sentiment_result['sentiment_score'],
                        sentiment_magnitude=sentiment_result['sentiment_magnitude'],
                        total_documents=total_documents,
                        keyword_embedding=kw_info['keyword_embedding'],
                        corpus_size=corpus_size,
                    )
                    
                    return keyword, data, sentiment_result, importance_result
                
                # Submit all keywords at once for better parallelism
                futures = {executor.submit(process_keyword, kw_info): kw_info for kw_info in keyword_batch_data}
                
                # Process results as they complete
                for idx, future in enumerate(as_completed(futures), 1):
                    try:
                        keyword, data, sentiment_result, importance_result = future.result()
                        
                        # Prepare sample snippets for storage
                        sample_snippets = []
                        for snippet_data in sentiment_result.get('sample_snippets', [])[:5]:
                            sample_snippets.append({
                                'text': snippet_data['snippet'],
                                'sentiment': snippet_data['sentiment'],
                                'classification': snippet_data['classification'],
                            })
                        
                        # Save to importance table
                        self.importance_repo.save_importance(
                            keyword=keyword,
                            analysis_date=analysis_date,
                            team_key=team,
                            importance_score=importance_result['importance'],
                            frequency=data['frequency'],
                            document_count=len(data['documents']),
                            source_diversity=len(set(doc['source_name'] for doc in data['documents'])),
                            velocity=importance_result['velocity'],
                            acceleration=importance_result['acceleration'],
                            sentiment_score=sentiment_result['sentiment_score'],
                            sentiment_magnitude=sentiment_result['sentiment_magnitude'],
                            positive_mentions=sentiment_result['positive_mentions'],
                            negative_mentions=sentiment_result['negative_mentions'],
                            neutral_mentions=sentiment_result['neutral_mentions'],
                            content_ids=data['content_ids'],
                            sample_snippets=sample_snippets,
                            extraction_method='enhanced_nlp',
                        )
                        
                        keywords_saved += 1
                        
                        # Log progress every 100 keywords
                        if idx % 100 == 0:
                            logger.info(f"Processed {idx}/{len(keyword_batch_data)} keywords...")
                    except Exception as e:
                        logger.error(f"Error processing keyword: {e}")
                
                keywords_processed = len(keyword_batch_data)
            
            # Clear cache after processing
            self.keyword_cache.clear()
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Importance calculation complete: "
                f"{keywords_processed} processed, "
                f"{keywords_saved} saved, "
                f"{processing_time_ms:.1f}ms"
            )
            
            return {
                'status': 'success',
                'keywords_processed': keywords_processed,
                'keywords_saved': keywords_saved,
                'processing_time_ms': processing_time_ms,
            }
        
        except Exception as e:
            logger.error(f"Importance calculation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'processing_time_ms': (time.time() - start_time) * 1000,
            }
    
    def process_batch(
        self,
        content_items: List[Dict],
        team_key: Optional[str] = None,
        calculate_importance: bool = True,
    ) -> Dict:
        """
        Process a batch of content items efficiently.
        
        Args:
            content_items: List of content dicts
            team_key: Team context
            calculate_importance: Whether to calculate importance after extraction
        
        Returns:
            Batch processing results
        """
        logger.info(f"Processing batch of {len(content_items)} items...")
        
        results = {
            'total': len(content_items),
            'successful': 0,
            'failed': 0,
            'keywords_extracted': 0,
            'keywords_stored': 0,
            'processing_time_ms': 0,
        }
        
        # Process each item
        for item in content_items:
            result = self.process_content(
                content_id=item['id'],
                title=item.get('title', ''),
                content=item.get('content', ''),
                source_type=item.get('source_type', 'unknown'),
                source_name=item.get('source_name', 'unknown'),
                published_date=item.get('published_date'),
                extraction_date=item.get('extraction_date'),
                team_key=team_key,
            )
            
            if result['status'] == 'success':
                results['successful'] += 1
                results['keywords_extracted'] += result['keywords_extracted']
                results['keywords_stored'] += result['keywords_stored']
            else:
                results['failed'] += 1
            
            results['processing_time_ms'] += result['processing_time_ms']
        
        # Calculate importance for all extracted keywords
        if calculate_importance and results['successful'] > 0:
            logger.info("Calculating importance for batch...")
            importance_result = self.calculate_importance_and_sentiment(
                team_key=team_key
            )
            results['importance_calculation'] = importance_result
            results['processing_time_ms'] += importance_result.get('processing_time_ms', 0)
        
        return results
    
    def generate_timeseries(
        self,
        team_key: Optional[str] = None,
        days: int = 30,
        min_importance: float = 30.0,
    ) -> Dict:
        """
        Generate time-series data for trending keywords.
        
        Args:
            team_key: Team context
            days: Number of days to include
            min_importance: Minimum importance to include
        
        Returns:
            Generation statistics
        """
        team = team_key or self.team_key
        logger.info(f"Generating time-series for team {team}, last {days} days...")
        
        start_time = time.time()
        
        try:
            # Get top keywords from today
            today = date.today()
            top_keywords = self.importance_repo.get_top_keywords(
                team_key=team,
                analysis_date=today,
                limit=100,
                min_importance=min_importance,
            )
            
            timeseries_created = 0
            
            for keyword_record in top_keywords:
                # Compute time-series
                ts = self.importance_repo.compute_timeseries_from_importance(
                    keyword=keyword_record.keyword,
                    team_key=team,
                    days=days,
                )
                
                if ts:
                    timeseries_created += 1
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Time-series generation complete: "
                f"{timeseries_created} created, "
                f"{processing_time_ms:.1f}ms"
            )
            
            return {
                'status': 'success',
                'keywords_analyzed': len(top_keywords),
                'timeseries_created': timeseries_created,
                'processing_time_ms': processing_time_ms,
            }
        
        except Exception as e:
            logger.error(f"Time-series generation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'processing_time_ms': (time.time() - start_time) * 1000,
            }
    
    def close(self):
        """Clean up resources."""
        self.keyword_repo.close()
        self.importance_repo.close()
        self.config_repo.close()
        self.content_repo.close()
