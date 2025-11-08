"""
Keyword extraction package.

Real-time keyword extraction from content with sophisticated NLP.
Includes importance calculation and sentiment analysis.
"""

from .models import (
    ExtractedKeywordModel,
    KeywordExtractionConfigModel,
    KeywordExtractionLogModel,
)
from .importance_models import (
    KeywordImportanceModel,
    KeywordTimeSeriesModel,
)
from .extractor import KeywordExtractor
from .repository import KeywordRepository, KeywordConfigRepository
from .importance_repository import ImportanceRepository
from .processor import RealtimeKeywordProcessor
from .enhanced_processor import EnhancedKeywordProcessor
from .importance import ImportanceCalculator, BM25Scorer
from .sentiment import SentimentAnalyzer, AspectBasedSentimentAnalyzer

__all__ = [
    # Base models
    'ExtractedKeywordModel',
    'KeywordExtractionConfigModel',
    'KeywordExtractionLogModel',
    # Importance models
    'KeywordImportanceModel',
    'KeywordTimeSeriesModel',
    # Extraction
    'KeywordExtractor',
    # Repositories
    'KeywordRepository',
    'KeywordConfigRepository',
    'ImportanceRepository',
    # Processors
    'RealtimeKeywordProcessor',
    'EnhancedKeywordProcessor',
    # Advanced NLP
    'ImportanceCalculator',
    'BM25Scorer',
    'SentimentAnalyzer',
    'AspectBasedSentimentAnalyzer',
]
