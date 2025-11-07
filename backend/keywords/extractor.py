"""
Real-time keyword extraction engine.

Combines TF-IDF, spaCy, and YAKE for sophisticated keyword extraction.
"""

import re
import time
from typing import List, Dict, Tuple, Optional
from datetime import datetime, date
from collections import Counter, defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordExtractor:
    """
    Multi-method keyword extractor.
    
    Combines:
    - TF-IDF for statistical relevance
    - spaCy for entities and noun phrases
    - YAKE for multi-word keyphrases
    """

    def __init__(
        self,
        tfidf_weight: float = 0.3,
        spacy_weight: float = 0.4,
        yake_weight: float = 0.3,
        max_phrase_length: int = 5,
    ):
        """
        Initialize keyword extractor.
        
        Args:
            tfidf_weight: Weight for TF-IDF scores (0-1)
            spacy_weight: Weight for spaCy scores (0-1)
            yake_weight: Weight for YAKE scores (0-1)
            max_phrase_length: Maximum words in a phrase
        """
        self.tfidf_weight = tfidf_weight
        self.spacy_weight = spacy_weight
        self.yake_weight = yake_weight
        self.max_phrase_length = max_phrase_length
        
        # Lazy loading of models
        self._nlp = None
        self._yake_extractor = None
        self._stop_words = None
    
    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            try:
                import spacy
                # Try medium model first, fall back to small
                try:
                    self._nlp = spacy.load("en_core_web_md")
                    logger.info("Loaded spaCy en_core_web_md model")
                except OSError:
                    self._nlp = spacy.load("en_core_web_sm")
                    logger.info("Loaded spaCy en_core_web_sm model")
            except Exception as e:
                logger.error(f"Failed to load spaCy model: {e}")
                raise
        return self._nlp
    
    @property
    def yake_extractor(self):
        """Lazy load YAKE extractor."""
        if self._yake_extractor is None:
            try:
                import yake
                self._yake_extractor = yake.KeywordExtractor(
                    lan="en",
                    n=self.max_phrase_length,
                    dedupLim=0.9,
                    top=100,  # Extract more, filter later
                    features=None
                )
                logger.info("Initialized YAKE extractor")
            except Exception as e:
                logger.error(f"Failed to initialize YAKE: {e}")
                # YAKE is optional, continue without it
                self._yake_extractor = None
        return self._yake_extractor
    
    @property
    def stop_words(self):
        """Get enhanced stop words list."""
        if self._stop_words is None:
            # Start with English stop words
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            self._stop_words = set(ENGLISH_STOP_WORDS)
            
            # Add tech/news specific stop words
            tech_stops = {
                'said', 'says', 'according', 'also', 'new', 'announced',
                'today', 'yesterday', 'report', 'reports', 'reported',
                'company', 'companies', 'tech', 'technology', 'http',
                'https', 'www', 'com', 'html', 'tweet', 'post', 'posted',
                'click', 'read', 'more', 'article', 'story', 'blog',
            }
            self._stop_words.update(tech_stops)
        
        return self._stop_words
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_tfidf_keywords(
        self,
        texts: List[str],
        top_n: int = 50
    ) -> Dict[str, float]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            texts: List of documents (for IDF calculation)
            top_n: Number of top keywords to return
        
        Returns:
            Dict of {keyword: tfidf_score}
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # Configure vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, self.max_phrase_length),
                stop_words=list(self.stop_words),
                min_df=1,  # Appear in at least 1 document
                max_df=0.9,  # Don't appear in >90% of documents
                lowercase=True,
                token_pattern=r'\b[a-z]{2,}\b',  # At least 2 chars
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get scores for the first document (or aggregate if multiple)
            if len(texts) == 1:
                scores = tfidf_matrix[0].toarray()[0]
            else:
                # Average scores across all documents
                scores = tfidf_matrix.mean(axis=0).A1
            
            # Create keyword: score mapping
            keyword_scores = {
                feature_names[i]: float(scores[i])
                for i in range(len(feature_names))
                if scores[i] > 0
            }
            
            # Sort and return top N
            sorted_keywords = sorted(
                keyword_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
            
            return dict(sorted_keywords)
        
        except Exception as e:
            logger.error(f"TF-IDF extraction failed: {e}")
            return {}
    
    def extract_spacy_keywords(
        self,
        text: str,
        top_n: int = 50
    ) -> List[Tuple[str, str, float]]:
        """
        Extract named entities and noun phrases using spaCy.
        
        Args:
            text: Text to analyze
            top_n: Number of top items to return
        
        Returns:
            List of (keyword, type, score) tuples
        """
        try:
            doc = self.nlp(text)
            
            results = []
            
            # Extract named entities
            entity_counts = Counter()
            entity_types = {}
            
            for ent in doc.ents:
                # Skip very short entities
                if len(ent.text) < 3:
                    continue
                
                # Normalize
                normalized = ent.text.lower().strip()
                
                # Skip stop words
                if normalized in self.stop_words:
                    continue
                
                entity_counts[normalized] += 1
                entity_types[normalized] = ent.label_
            
            # Convert entity counts to scores (normalize by max count)
            max_count = max(entity_counts.values()) if entity_counts else 1
            for entity, count in entity_counts.items():
                score = count / max_count
                entity_type = entity_types[entity]
                results.append((entity, f"entity_{entity_type}", score))
            
            # Extract noun phrases
            noun_phrase_counts = Counter()
            
            for chunk in doc.noun_chunks:
                # Clean the chunk
                phrase = chunk.text.lower().strip()
                
                # Skip if too short or too long
                word_count = len(phrase.split())
                if word_count < 2 or word_count > self.max_phrase_length:
                    continue
                
                # Skip if starts/ends with stop word
                words = phrase.split()
                if words[0] in self.stop_words or words[-1] in self.stop_words:
                    continue
                
                noun_phrase_counts[phrase] += 1
            
            # Convert noun phrase counts to scores
            max_count = max(noun_phrase_counts.values()) if noun_phrase_counts else 1
            for phrase, count in noun_phrase_counts.items():
                score = count / max_count
                results.append((phrase, "phrase", score))
            
            # Sort by score and return top N
            results.sort(key=lambda x: x[2], reverse=True)
            return results[:top_n]
        
        except Exception as e:
            logger.error(f"spaCy extraction failed: {e}")
            return []
    
    def extract_yake_keywords(
        self,
        text: str,
        top_n: int = 50
    ) -> Dict[str, float]:
        """
        Extract keyphrases using YAKE.
        
        Args:
            text: Text to analyze
            top_n: Number of top keywords to return
        
        Returns:
            Dict of {keyword: score}
        """
        if self.yake_extractor is None:
            return {}
        
        try:
            # YAKE returns (keyword, score) where lower score = better
            keywords = self.yake_extractor.extract_keywords(text)
            
            # Normalize scores to 0-1 range (invert because lower is better)
            if keywords:
                max_score = max(score for _, score in keywords)
                normalized = {
                    kw.lower(): 1.0 - (score / max_score)
                    for kw, score in keywords
                }
                
                # Return top N
                sorted_keywords = sorted(
                    normalized.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:top_n]
                
                return dict(sorted_keywords)
            
            return {}
        
        except Exception as e:
            logger.error(f"YAKE extraction failed: {e}")
            return {}
    
    def merge_and_rank(
        self,
        tfidf_keywords: Dict[str, float],
        spacy_keywords: List[Tuple[str, str, float]],
        yake_keywords: Dict[str, float],
        tfidf_weight: float = None,
        spacy_weight: float = None,
        yake_weight: float = None,
    ) -> List[Dict[str, any]]:
        """
        Merge keywords from all methods and compute combined scores.
        
        Args:
            tfidf_keywords: {keyword: score}
            spacy_keywords: [(keyword, type, score)]
            yake_keywords: {keyword: score}
            tfidf_weight: Weight for TF-IDF scores (uses instance default if None)
            spacy_weight: Weight for spaCy scores (uses instance default if None)
            yake_weight: Weight for YAKE scores (uses instance default if None)
        
        Returns:
            List of keyword dicts with combined scores
        """
        # Use provided weights or fall back to instance weights
        tfidf_w = tfidf_weight if tfidf_weight is not None else self.tfidf_weight
        spacy_w = spacy_weight if spacy_weight is not None else self.spacy_weight
        yake_w = yake_weight if yake_weight is not None else self.yake_weight
        
        # Collect all keywords
        all_keywords = {}
        
        # Add TF-IDF keywords
        for keyword, score in tfidf_keywords.items():
            if keyword not in all_keywords:
                all_keywords[keyword] = {
                    'keyword': keyword,
                    'type': 'single' if ' ' not in keyword else 'phrase',
                    'entity_type': None,
                    'tfidf_score': score,
                    'spacy_score': 0.0,
                    'yake_score': 0.0,
                }
            else:
                all_keywords[keyword]['tfidf_score'] = score
        
        # Add spaCy keywords
        for keyword, kw_type, score in spacy_keywords:
            if keyword not in all_keywords:
                all_keywords[keyword] = {
                    'keyword': keyword,
                    'type': kw_type.split('_')[0],  # 'entity' or 'phrase'
                    'entity_type': kw_type.split('_')[1] if '_' in kw_type else None,
                    'tfidf_score': 0.0,
                    'spacy_score': score,
                    'yake_score': 0.0,
                }
            else:
                all_keywords[keyword]['spacy_score'] = score
                if kw_type.startswith('entity_'):
                    all_keywords[keyword]['type'] = 'entity'
                    all_keywords[keyword]['entity_type'] = kw_type.split('_')[1]
        
        # Add YAKE keywords
        for keyword, score in yake_keywords.items():
            if keyword not in all_keywords:
                all_keywords[keyword] = {
                    'keyword': keyword,
                    'type': 'single' if ' ' not in keyword else 'phrase',
                    'entity_type': None,
                    'tfidf_score': 0.0,
                    'spacy_score': 0.0,
                    'yake_score': score,
                }
            else:
                all_keywords[keyword]['yake_score'] = score
        
        # Compute combined scores
        for kw_data in all_keywords.values():
            combined = (
                kw_data['tfidf_score'] * tfidf_w +
                kw_data['spacy_score'] * spacy_w +
                kw_data['yake_score'] * yake_w
            )
            kw_data['relevance_score'] = combined
        
        # Convert to list and sort by relevance
        results = list(all_keywords.values())
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results
    
    def extract(
        self,
        text: str,
        title: str = "",
        context_docs: List[str] = None,
        max_keywords: int = 50,
        tfidf_weight: float = None,
        spacy_weight: float = None,
        yake_weight: float = None,
    ) -> List[Dict[str, any]]:
        """
        Extract keywords from text using all methods.
        
        Args:
            text: Main text to analyze
            title: Document title (will be included in analysis)
            context_docs: Additional documents for TF-IDF context
            max_keywords: Maximum keywords to return
            tfidf_weight: Weight for TF-IDF scores (uses instance default if None)
            spacy_weight: Weight for spaCy scores (uses instance default if None)
            yake_weight: Weight for YAKE scores (uses instance default if None)
        
        Returns:
            List of keyword dicts with scores
        """
        start_time = time.time()
        
        # Preprocess
        clean_text = self.preprocess_text(text)
        clean_title = self.preprocess_text(title) if title else ""
        
        # Combine title and text (title gets more weight)
        full_text = f"{clean_title} {clean_title} {clean_text}"
        
        # Prepare documents for TF-IDF
        if context_docs:
            tfidf_docs = [full_text] + [self.preprocess_text(d) for d in context_docs]
        else:
            tfidf_docs = [full_text]
        
        # Extract using each method
        logger.info("Extracting with TF-IDF...")
        tfidf_keywords = self.extract_tfidf_keywords(tfidf_docs)
        
        logger.info("Extracting with spaCy...")
        spacy_keywords = self.extract_spacy_keywords(full_text)
        
        logger.info("Extracting with YAKE...")
        yake_keywords = self.extract_yake_keywords(full_text)
        
        # Merge and rank
        logger.info("Merging and ranking...")
        merged_keywords = self.merge_and_rank(
            tfidf_keywords,
            spacy_keywords,
            yake_keywords,
            tfidf_weight=tfidf_weight,
            spacy_weight=spacy_weight,
            yake_weight=yake_weight,
        )
        
        # Limit results
        merged_keywords = merged_keywords[:max_keywords]
        
        elapsed = time.time() - start_time
        logger.info(f"Extracted {len(merged_keywords)} keywords in {elapsed:.2f}s")
        
        return merged_keywords
