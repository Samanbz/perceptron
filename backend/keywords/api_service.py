"""
API service layer for keyword data.

Transforms database models into Pydantic API models
defined in api_models.py.
"""

from typing import List, Optional, Dict
from datetime import date, timedelta
import logging

from keywords.importance_repository import ImportanceRepository
from storage.repository import ContentRepository
from teams.repository import TeamRepository
from api_models import (
    WordCloudResponse,
    KeywordData,
    KeywordSentiment,
    KeywordMetrics,
    SentimentBreakdown,
    DocumentReference,
    TimeSeriesResponse,
    KeywordTimeSeries,
    TimePoint,
)


logger = logging.getLogger(__name__)


class KeywordAPIService:
    """
    Service layer for keyword API endpoints.
    
    Bridges database layer and API response models.
    """
    
    def __init__(
        self,
        importance_repo: Optional[ImportanceRepository] = None,
        content_repo: Optional[ContentRepository] = None,
        team_repo: Optional[TeamRepository] = None,
    ):
        """Initialize API service."""
        self.importance_repo = importance_repo or ImportanceRepository()
        self.content_repo = content_repo or ContentRepository()
        self.team_repo = team_repo or TeamRepository()
    
    def get_word_cloud_data(
        self,
        team_key: str,
        target_date: Optional[date] = None,
        limit: int = 50,
        min_importance: float = 30.0,
    ) -> WordCloudResponse:
        """
        Get word cloud data for a team and date.
        
        Args:
            team_key: Team identifier
            target_date: Date to get data for (defaults to today)
            limit: Maximum keywords to return
            min_importance: Minimum importance threshold
        
        Returns:
            WordCloudResponse with complete keyword data
        """
        if target_date is None:
            target_date = date.today()
        
        logger.info(f"Getting word cloud for team {team_key} on {target_date}")
        
        # Get team info
        team = self.team_repo.get_team_by_key(team_key)
        if not team:
            logger.warning(f"Team {team_key} not found")
            return self._empty_word_cloud(team_key, target_date)
        
        # Get top keywords for this date and team
        keyword_records = self.importance_repo.get_top_keywords(
            team_key=team_key,
            analysis_date=target_date,
            limit=limit,
            min_importance=min_importance,
        )
        
        if not keyword_records:
            logger.info(f"No keywords found for {team_key} on {target_date}")
            return self._empty_word_cloud(team_key, target_date, team.team_name)
        
        # Transform to API models
        keyword_data_list = []
        total_documents = 0
        
        for record in keyword_records:
            # Build sentiment
            sentiment = KeywordSentiment(
                score=record.sentiment_score,
                magnitude=record.sentiment_magnitude,
                breakdown=SentimentBreakdown(
                    positive=record.positive_mentions,
                    negative=record.negative_mentions,
                    neutral=record.neutral_mentions,
                )
            )
            
            # Build metrics
            metrics = KeywordMetrics(
                frequency=record.frequency,
                document_count=record.document_count,
                source_diversity=record.source_diversity,
                velocity=record.velocity,
            )
            
            # Get document references
            documents = self._get_document_references(
                content_ids=record.content_ids or [],
                snippets=record.sample_snippets or [],
                limit=10,
            )
            
            total_documents += record.document_count
            
            # Build keyword data
            keyword_data = KeywordData(
                keyword=record.keyword,
                date=record.date.isoformat(),
                importance=record.importance_score,
                sentiment=sentiment,
                metrics=metrics,
                documents=documents,
            )
            
            keyword_data_list.append(keyword_data)
        
        return WordCloudResponse(
            team_key=team_key,
            team_name=team.team_name,
            date_range={
                "start": target_date.isoformat(),
                "end": target_date.isoformat(),
            },
            keywords=keyword_data_list,
            total_keywords=len(keyword_data_list),
            total_documents=total_documents,
        )
    
    def get_keyword_timeseries(
        self,
        team_key: str,
        keyword: str,
        days: int = 30,
    ) -> Optional[TimeSeriesResponse]:
        """
        Get time-series data for a specific keyword.
        
        Args:
            team_key: Team identifier
            keyword: Keyword to get history for
            days: Number of days to include
        
        Returns:
            TimeSeriesResponse or None if no data
        """
        logger.info(f"Getting time-series for '{keyword}' (team: {team_key})")
        
        # Get team info
        team = self.team_repo.get_team_by_key(team_key)
        if not team:
            logger.warning(f"Team {team_key} not found")
            return None
        
        # Try to get pre-computed time-series
        timeseries = self.importance_repo.get_timeseries(
            keyword=keyword,
            team_key=team_key,
            period='day'
        )
        
        if timeseries:
            # Use pre-computed data
            data_points = [
                TimePoint(
                    date=d,
                    importance=imp,
                    sentiment=sent,
                    frequency=freq
                )
                for d, imp, sent, freq in zip(
                    timeseries.dates,
                    timeseries.importance_values,
                    timeseries.sentiment_values,
                    timeseries.frequency_values,
                )
            ]
            
            keyword_ts = KeywordTimeSeries(
                keyword=keyword,
                trend=timeseries.trend,
                data_points=data_points,
                summary={
                    "avg_importance": timeseries.avg_importance,
                    "max_importance": timeseries.max_importance,
                }
            )
        else:
            # Compute on-the-fly from importance records
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            history = self.importance_repo.get_keyword_history(
                keyword=keyword,
                team_key=team_key,
                start_date=start_date,
                end_date=end_date,
            )
            
            if not history:
                logger.info(f"No history found for keyword '{keyword}'")
                return None
            
            # Build data points
            data_points = [
                TimePoint(
                    date=record.date.isoformat(),
                    importance=record.importance_score,
                    sentiment=record.sentiment_score,
                    frequency=record.frequency,
                )
                for record in history
            ]
            
            # Calculate trend
            if len(history) >= 3:
                recent_avg = sum(r.importance_score for r in history[-3:]) / 3
                older_avg = sum(r.importance_score for r in history[:3]) / 3
                
                if recent_avg > older_avg * 1.5:
                    trend = 'rising'
                elif recent_avg < older_avg * 0.7:
                    trend = 'falling'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            importance_values = [r.importance_score for r in history]
            
            keyword_ts = KeywordTimeSeries(
                keyword=keyword,
                trend=trend,
                data_points=data_points,
                summary={
                    "avg_importance": sum(importance_values) / len(importance_values),
                    "max_importance": max(importance_values),
                }
            )
        
        return TimeSeriesResponse(
            team_key=team_key,
            period={
                "start": data_points[0].date if data_points else "",
                "end": data_points[-1].date if data_points else "",
                "granularity": "day",
            },
            keywords=[keyword_ts],
        )
    
    def get_trending_keywords_timeseries(
        self,
        team_key: str,
        limit: int = 10,
        days: int = 30,
    ) -> TimeSeriesResponse:
        """
        Get time-series for top trending keywords.
        
        Args:
            team_key: Team identifier
            limit: Number of keywords to include
            days: Number of days to include
        
        Returns:
            TimeSeriesResponse with multiple keywords
        """
        logger.info(f"Getting trending keywords for team {team_key}")
        
        # Get top keywords from today
        today = date.today()
        top_keywords = self.importance_repo.get_top_keywords(
            team_key=team_key,
            analysis_date=today,
            limit=limit,
            min_importance=30.0,
        )
        
        keyword_timeseries_list = []
        
        for record in top_keywords:
            ts_response = self.get_keyword_timeseries(
                team_key=team_key,
                keyword=record.keyword,
                days=days,
            )
            
            if ts_response and ts_response.keywords:
                keyword_timeseries_list.append(ts_response.keywords[0])
        
        end_date = today
        start_date = end_date - timedelta(days=days)
        
        return TimeSeriesResponse(
            team_key=team_key,
            period={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "granularity": "day",
            },
            keywords=keyword_timeseries_list,
        )
    
    def _get_document_references(
        self,
        content_ids: List[int],
        snippets: List[Dict],
        limit: int = 10,
    ) -> List[DocumentReference]:
        """
        Get document references from content IDs.
        
        Args:
            content_ids: List of content IDs
            snippets: Sample snippets with sentiment
            limit: Maximum documents to return
        
        Returns:
            List of DocumentReference objects
        """
        if not content_ids:
            return []
        
        documents = []
        snippet_index = 0
        
        for content_id in content_ids[:limit]:
            try:
                # Get content from data lake
                content = self.content_repo.get_content_by_id(content_id)
                
                if content:
                    # Get corresponding snippet if available
                    snippet_text = ""
                    if snippet_index < len(snippets):
                        snippet_text = snippets[snippet_index].get('text', '')
                        snippet_index += 1
                    
                    documents.append(DocumentReference(
                        content_id=content.id,
                        title=content.title,
                        source_name=content.source_name,
                        published_date=content.published_date.isoformat() if content.published_date else "",
                        url=content.url,
                        snippet=snippet_text[:300] + '...' if len(snippet_text) > 300 else snippet_text,
                    ))
            except Exception as e:
                logger.warning(f"Failed to get content {content_id}: {e}")
                continue
        
        return documents
    
    def _empty_word_cloud(
        self,
        team_key: str,
        target_date: date,
        team_name: str = "Unknown Team"
    ) -> WordCloudResponse:
        """Return empty word cloud response."""
        return WordCloudResponse(
            team_key=team_key,
            team_name=team_name,
            date_range={
                "start": target_date.isoformat(),
                "end": target_date.isoformat(),
            },
            keywords=[],
            total_keywords=0,
            total_documents=0,
        )
    
    def close(self):
        """Clean up resources."""
        self.importance_repo.close()
        self.content_repo.close()
        self.team_repo.close()
