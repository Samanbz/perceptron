"""
Sophisticated importance calculation for keywords.

Uses multiple signals with state-of-the-art NLP techniques:
1. Frequency-based relevance (TF-IDF, BM25)
2. Contextual embeddings (sentence transformers)
3. Named Entity Recognition weighting
4. Temporal dynamics (velocity, acceleration)
5. Source diversity and credibility
6. Sentiment magnitude
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from collections import defaultdict
import logging

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


logger = logging.getLogger(__name__)


class ImportanceCalculator:
    """
    Calculate keyword importance using multiple sophisticated signals.
    
    Importance Score (0-100) is calculated from:
    - Frequency & Distribution (25%): How often and how widely mentioned
    - Contextual Relevance (20%): Semantic importance in context
    - Named Entity Boost (15%): Boost for recognized entities
    - Temporal Dynamics (20%): Velocity and acceleration
    - Source Diversity (10%): Mentioned across different sources
    - Sentiment Magnitude (10%): Stronger sentiment = more important
    """
    
    def __init__(
        self,
        use_embeddings: bool = True,
        use_ner: bool = True,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize importance calculator.
        
        Args:
            use_embeddings: Use sentence embeddings for contextual relevance
            use_ner: Use Named Entity Recognition for entity boost
            embedding_model: Sentence transformer model name
        """
        self.use_embeddings = use_embeddings and SENTENCE_TRANSFORMERS_AVAILABLE
        self.use_ner = use_ner and SPACY_AVAILABLE
        
        # Load models
        self.embedding_model = None
        if self.use_embeddings:
            try:
                logger.info(f"Loading sentence transformer: {embedding_model}")
                self.embedding_model = SentenceTransformer(embedding_model)
            except Exception as e:
                logger.warning(f"Failed to load embeddings: {e}")
                self.use_embeddings = False
        
        self.nlp = None
        if self.use_ner:
            try:
                logger.info("Loading spaCy for NER")
                self.nlp = spacy.load("en_core_web_md")
            except Exception as e:
                logger.warning(f"Failed to load spaCy: {e}")
                self.use_ner = False
        
        # Weights for each signal
        self.weights = {
            'frequency_distribution': 0.25,
            'contextual_relevance': 0.20,
            'entity_boost': 0.15,
            'temporal_dynamics': 0.20,
            'source_diversity': 0.10,
            'sentiment_magnitude': 0.10,
        }
    
    def batch_encode_keywords(self, keywords: List[str]) -> Dict[str, np.ndarray]:
        """
        Batch encode all keywords at once for efficiency.
        
        Args:
            keywords: List of keywords to encode
        
        Returns:
            Dict mapping keyword to embedding vector
        """
        if not self.use_embeddings or not keywords:
            return {}
        
        try:
            logger.info(f"Batch encoding {len(keywords)} keywords...")
            # Encode all keywords in one call (much faster!)
            embeddings = self.embedding_model.encode(
                keywords,
                show_progress_bar=False,
                batch_size=32  # Process 32 at a time
            )
            
            # Return as dict for easy lookup
            return {kw: emb for kw, emb in zip(keywords, embeddings)}
        
        except Exception as e:
            logger.warning(f"Batch encoding failed: {e}")
            return {}
    
    def calculate_frequency_score(
        self,
        frequency: int,
        document_count: int,
        total_documents: int,
        corpus_size: int
    ) -> float:
        """
        Calculate frequency-based importance using TF-IDF-like scoring.
        
        Args:
            frequency: Total mentions of keyword
            document_count: Number of documents containing keyword
            total_documents: Total documents in corpus
            corpus_size: Total words in corpus
        
        Returns:
            Score 0-100
        """
        # Term frequency (normalized)
        tf = frequency / max(corpus_size, 1)
        
        # Inverse document frequency
        idf = np.log((total_documents + 1) / (document_count + 1))
        
        # TF-IDF score
        tfidf = tf * idf
        
        # Normalize to 0-100 (using log scale)
        score = min(100, (1 + np.log1p(tfidf * 1000)) * 20)
        
        return float(score)
    
    def calculate_contextual_relevance(
        self,
        keyword: str,
        snippets: List[str],
        document_topics: Optional[List[str]] = None,
        keyword_embedding: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate contextual relevance using embeddings.
        
        Measures semantic centrality: how central is this keyword to the
        document themes?
        
        Args:
            keyword: The keyword
            snippets: Text snippets containing the keyword
            document_topics: Main topics/themes of documents
            keyword_embedding: Pre-computed embedding (for batch processing)
        
        Returns:
            Score 0-100
        """
        if not self.use_embeddings or not snippets:
            return 50.0  # Default neutral score
        
        try:
            # Get keyword embedding (use pre-computed if available)
            if keyword_embedding is None:
                keyword_embedding = self.embedding_model.encode([keyword], show_progress_bar=False)[0]
            
            # Get snippet embeddings (batch encode for efficiency)
            snippet_embeddings = self.embedding_model.encode(
                snippets[:10],
                show_progress_bar=False,
                batch_size=32
            )
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            
            similarities = cosine_similarity(
                [keyword_embedding],
                snippet_embeddings
            )[0]
            
            # Average similarity (higher = more contextually relevant)
            avg_similarity = np.mean(similarities)
            
            # Normalize to 0-100
            score = (avg_similarity + 1) * 50  # Cosine is -1 to 1
            
            return float(min(100, max(0, score)))
        
        except Exception as e:
            logger.warning(f"Contextual relevance calculation failed: {e}")
            return 50.0
    
    def calculate_entity_boost(
        self,
        keyword: str,
        entity_types: Optional[List[str]] = None
    ) -> float:
        """
        Calculate boost for named entities.
        
        Recognized entities (PERSON, ORG, PRODUCT, etc.) get importance boost.
        
        Args:
            keyword: The keyword to check
            entity_types: List of entity types this keyword represents
        
        Returns:
            Score 0-100
        """
        if not self.use_ner:
            return 50.0
        
        try:
            doc = self.nlp(keyword)
            
            # Check if it's a named entity
            if doc.ents:
                entity_label = doc.ents[0].label_
                
                # High-value entities
                high_value = ['PERSON', 'ORG', 'PRODUCT', 'GPE', 'EVENT', 'LAW']
                medium_value = ['MONEY', 'DATE', 'CARDINAL', 'NORP']
                
                if entity_label in high_value:
                    return 85.0
                elif entity_label in medium_value:
                    return 65.0
                else:
                    return 55.0
            
            # Check if it's a noun chunk (multi-word technical term)
            if len(keyword.split()) > 1:
                return 60.0  # Multi-word phrases get slight boost
            
            return 50.0
        
        except Exception as e:
            logger.warning(f"Entity boost calculation failed: {e}")
            return 50.0
    
    def calculate_temporal_dynamics(
        self,
        current_frequency: int,
        previous_frequencies: List[int],
        window_days: int = 7
    ) -> Tuple[float, float, float]:
        """
        Calculate temporal dynamics: velocity and acceleration.
        
        Args:
            current_frequency: Today's frequency
            previous_frequencies: Frequencies from previous days (ordered)
            window_days: Size of rolling window
        
        Returns:
            (score, velocity, acceleration)
            - score: 0-100 based on trend strength
            - velocity: Rate of change (percentage)
            - acceleration: Change in velocity
        """
        if not previous_frequencies:
            return 50.0, 0.0, 0.0
        
        # Calculate velocity (rate of change)
        if len(previous_frequencies) >= 1:
            prev_avg = np.mean(previous_frequencies[-window_days:])
            if prev_avg > 0:
                velocity = ((current_frequency - prev_avg) / prev_avg) * 100
            else:
                velocity = 100.0 if current_frequency > 0 else 0.0
        else:
            velocity = 0.0
        
        # Calculate acceleration (change in velocity)
        if len(previous_frequencies) >= 2:
            recent_window = previous_frequencies[-window_days//2:]
            older_window = previous_frequencies[-window_days:-window_days//2] if len(previous_frequencies) > window_days//2 else []
            
            if older_window:
                recent_avg = np.mean(recent_window)
                older_avg = np.mean(older_window)
                if older_avg > 0:
                    prev_velocity = ((recent_avg - older_avg) / older_avg) * 100
                    acceleration = velocity - prev_velocity
                else:
                    acceleration = velocity
            else:
                acceleration = 0.0
        else:
            acceleration = 0.0
        
        # Score based on velocity and acceleration
        # Rising trends (positive velocity) score higher
        # Accelerating trends score even higher
        base_score = 50.0
        velocity_score = min(30, max(-30, velocity / 2))  # ±30 points
        acceleration_score = min(20, max(-20, acceleration / 5))  # ±20 points
        
        score = base_score + velocity_score + acceleration_score
        score = min(100, max(0, score))
        
        return float(score), float(velocity), float(acceleration)
    
    def calculate_source_diversity_score(
        self,
        source_count: int,
        max_possible_sources: int = 20
    ) -> float:
        """
        Calculate score based on source diversity.
        
        Keywords mentioned across many sources are more important.
        
        Args:
            source_count: Number of unique sources
            max_possible_sources: Maximum sources in system
        
        Returns:
            Score 0-100
        """
        # Logarithmic scale (diminishing returns)
        if source_count == 0:
            return 0.0
        
        # Use log scale to reduce impact of very high counts
        normalized = min(1.0, source_count / max_possible_sources)
        score = (1 + np.log1p(normalized * 10)) * 30
        
        return float(min(100, score))
    
    def calculate_sentiment_magnitude_score(
        self,
        sentiment_magnitude: float,
        sentiment_score: float
    ) -> float:
        """
        Calculate importance based on sentiment strength.
        
        Strong sentiment (very positive or very negative) indicates importance.
        
        Args:
            sentiment_magnitude: Strength of sentiment (0-1)
            sentiment_score: Polarity of sentiment (-1 to 1)
        
        Returns:
            Score 0-100
        """
        # Strong sentiment (regardless of polarity) = important
        # Controversial topics (mixed sentiment) also important
        
        base_score = sentiment_magnitude * 100
        
        # Boost for extreme sentiment (very positive or very negative)
        extremity = abs(sentiment_score)
        extremity_boost = extremity * 20
        
        score = base_score + extremity_boost
        return float(min(100, score))
    
    def calculate_importance(
        self,
        keyword: str,
        frequency: int,
        document_count: int,
        source_diversity: int,
        snippets: List[str],
        previous_frequencies: List[int],
        sentiment_score: float = 0.0,
        sentiment_magnitude: float = 0.0,
        total_documents: int = 100,
        corpus_size: int = 10000,
        entity_types: Optional[List[str]] = None,
        keyword_embedding: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Calculate overall importance score using all signals.
        
        Args:
            keyword: The keyword
            frequency: Total mentions
            document_count: Number of documents
            source_diversity: Number of unique sources
            snippets: Text snippets containing keyword
            previous_frequencies: Historical frequency data
            sentiment_score: Sentiment polarity (-1 to 1)
            sentiment_magnitude: Sentiment strength (0 to 1)
            total_documents: Total docs in corpus
            corpus_size: Total words in corpus
            entity_types: Entity type labels
            keyword_embedding: Pre-computed embedding (for batch processing)
        
        Returns:
            Dict with overall score and component scores
        """
        # Calculate each component
        freq_score = self.calculate_frequency_score(
            frequency, document_count, total_documents, corpus_size
        )
        
        context_score = self.calculate_contextual_relevance(
            keyword, snippets, keyword_embedding=keyword_embedding
        )
        
        entity_score = self.calculate_entity_boost(keyword, entity_types)
        
        temporal_score, velocity, acceleration = self.calculate_temporal_dynamics(
            frequency, previous_frequencies
        )
        
        diversity_score = self.calculate_source_diversity_score(source_diversity)
        
        sentiment_score_component = self.calculate_sentiment_magnitude_score(
            sentiment_magnitude, sentiment_score
        )
        
        # Weighted combination
        importance = (
            self.weights['frequency_distribution'] * freq_score +
            self.weights['contextual_relevance'] * context_score +
            self.weights['entity_boost'] * entity_score +
            self.weights['temporal_dynamics'] * temporal_score +
            self.weights['source_diversity'] * diversity_score +
            self.weights['sentiment_magnitude'] * sentiment_score_component
        )
        
        return {
            'importance': round(importance, 2),
            'components': {
                'frequency_distribution': round(freq_score, 2),
                'contextual_relevance': round(context_score, 2),
                'entity_boost': round(entity_score, 2),
                'temporal_dynamics': round(temporal_score, 2),
                'source_diversity': round(diversity_score, 2),
                'sentiment_magnitude': round(sentiment_score_component, 2),
            },
            'velocity': round(velocity, 2),
            'acceleration': round(acceleration, 2),
        }


class BM25Scorer:
    """
    BM25 (Best Matching 25) scoring for keyword relevance.
    
    State-of-the-art probabilistic relevance framework.
    More sophisticated than TF-IDF.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Args:
            k1: Term frequency saturation parameter (1.2-2.0)
            b: Length normalization parameter (0.75 is standard)
        """
        self.k1 = k1
        self.b = b
        self.avg_doc_length = 0
        self.doc_lengths = []
        self.document_frequencies = defaultdict(int)
        self.num_documents = 0
    
    def fit(self, documents: List[List[str]]):
        """
        Fit BM25 on document corpus.
        
        Args:
            documents: List of documents (each doc is list of terms)
        """
        self.num_documents = len(documents)
        self.doc_lengths = [len(doc) for doc in documents]
        self.avg_doc_length = np.mean(self.doc_lengths) if self.doc_lengths else 0
        
        # Calculate document frequencies
        for doc in documents:
            unique_terms = set(doc)
            for term in unique_terms:
                self.document_frequencies[term] += 1
    
    def score(
        self,
        query_terms: List[str],
        document: List[str],
        doc_length: Optional[int] = None
    ) -> float:
        """
        Calculate BM25 score for a document given query terms.
        
        Args:
            query_terms: Terms to score
            document: Document terms
            doc_length: Document length (calculated if not provided)
        
        Returns:
            BM25 score
        """
        if doc_length is None:
            doc_length = len(document)
        
        score = 0.0
        
        for term in query_terms:
            if term not in document:
                continue
            
            # Term frequency in document
            tf = document.count(term)
            
            # Document frequency
            df = self.document_frequencies.get(term, 0)
            
            # IDF component
            idf = np.log((self.num_documents - df + 0.5) / (df + 0.5) + 1.0)
            
            # Length normalization
            length_norm = (
                (tf * (self.k1 + 1)) /
                (tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length))
            )
            
            score += idf * length_norm
        
        return score
