"""
Sophisticated sentiment analysis for keywords in context.

Uses multiple approaches:
1. VADER: Lexicon-based sentiment (social media optimized)
2. Contextual sentiment: Analyzes sentiment around keyword in text
3. Aspect-based sentiment: Keyword-specific sentiment
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import logging

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyze sentiment around keywords using multiple methods.
    
    Returns:
    - sentiment_score: -1 (negative) to +1 (positive)
    - sentiment_magnitude: 0 (weak) to 1 (strong)
    - breakdown: positive/negative/neutral mention counts
    """
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        self.vader = None
        if VADER_AVAILABLE:
            try:
                self.vader = SentimentIntensityAnalyzer()
                logger.info("VADER sentiment analyzer loaded")
            except Exception as e:
                logger.warning(f"Failed to load VADER: {e}")
        
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_md")
                logger.info("spaCy loaded for contextual sentiment")
            except Exception as e:
                logger.warning(f"Failed to load spaCy: {e}")
    
    def extract_keyword_context(
        self,
        text: str,
        keyword: str,
        window: int = 50
    ) -> List[str]:
        """
        Extract text snippets around keyword mentions.
        
        Args:
            text: Full text
            keyword: Keyword to find
            window: Characters before/after keyword
        
        Returns:
            List of context snippets
        """
        snippets = []
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        
        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            
            # Extract context window
            context_start = max(0, pos - window)
            context_end = min(len(text), pos + len(keyword) + window)
            snippet = text[context_start:context_end]
            
            snippets.append(snippet)
            start = pos + 1
        
        return snippets
    
    def analyze_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict with sentiment scores
        """
        if not self.vader:
            return {
                'compound': 0.0,
                'pos': 0.0,
                'neu': 1.0,
                'neg': 0.0
            }
        
        try:
            scores = self.vader.polarity_scores(text)
            return scores
        except Exception as e:
            logger.warning(f"VADER analysis failed: {e}")
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
    
    def analyze_contextual_sentiment(
        self,
        snippets: List[str]
    ) -> Tuple[float, float]:
        """
        Analyze sentiment of snippets around keyword.
        
        Args:
            snippets: Text snippets containing keyword
        
        Returns:
            (sentiment_score, magnitude)
        """
        if not snippets:
            return 0.0, 0.0
        
        sentiment_scores = []
        magnitudes = []
        
        for snippet in snippets:
            vader_scores = self.analyze_vader(snippet)
            
            # Compound score (-1 to 1)
            sentiment_scores.append(vader_scores['compound'])
            
            # Magnitude: max of pos/neg scores
            magnitude = max(vader_scores['pos'], vader_scores['neg'])
            magnitudes.append(magnitude)
        
        # Average across all mentions
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        avg_magnitude = sum(magnitudes) / len(magnitudes)
        
        return avg_sentiment, avg_magnitude
    
    def classify_sentiment(
        self,
        sentiment_score: float,
        magnitude_threshold: float = 0.05
    ) -> str:
        """
        Classify sentiment as positive/negative/neutral.
        
        Args:
            sentiment_score: -1 to 1
            magnitude_threshold: Minimum magnitude to be non-neutral
        
        Returns:
            'positive', 'negative', or 'neutral'
        """
        if abs(sentiment_score) < magnitude_threshold:
            return 'neutral'
        elif sentiment_score > 0:
            return 'positive'
        else:
            return 'negative'
    
    def analyze_keyword_sentiment(
        self,
        keyword: str,
        documents: List[Dict[str, str]],
        context_window: int = 100
    ) -> Dict[str, any]:
        """
        Analyze sentiment around a keyword across multiple documents.
        
        Args:
            keyword: Keyword to analyze
            documents: List of dicts with 'content' and optionally 'title'
            context_window: Characters around keyword to analyze
        
        Returns:
            Dict with:
            - sentiment_score: -1 to 1
            - sentiment_magnitude: 0 to 1
            - positive_mentions: count
            - negative_mentions: count
            - neutral_mentions: count
            - snippets: sample snippets with sentiment
        """
        all_snippets = []
        sentiment_classifications = defaultdict(int)
        snippet_sentiments = []
        
        for doc in documents:
            text = doc.get('content', '')
            title = doc.get('title', '')
            
            # Extract context around keyword
            snippets = self.extract_keyword_context(
                text + ' ' + title,
                keyword,
                window=context_window
            )
            
            for snippet in snippets:
                # Analyze this snippet
                vader_scores = self.analyze_vader(snippet)
                sentiment = vader_scores['compound']
                magnitude = max(vader_scores['pos'], vader_scores['neg'])
                
                classification = self.classify_sentiment(sentiment)
                sentiment_classifications[classification] += 1
                
                all_snippets.append(snippet)
                snippet_sentiments.append({
                    'snippet': snippet[:200] + '...' if len(snippet) > 200 else snippet,
                    'sentiment': round(sentiment, 3),
                    'magnitude': round(magnitude, 3),
                    'classification': classification,
                })
        
        if not all_snippets:
            return {
                'sentiment_score': 0.0,
                'sentiment_magnitude': 0.0,
                'positive_mentions': 0,
                'negative_mentions': 0,
                'neutral_mentions': 0,
                'total_mentions': 0,
                'sample_snippets': [],
            }
        
        # Calculate overall sentiment
        overall_sentiment, overall_magnitude = self.analyze_contextual_sentiment(
            all_snippets
        )
        
        # Get sample snippets (most extreme positive and negative)
        snippet_sentiments.sort(key=lambda x: abs(x['sentiment']), reverse=True)
        sample_snippets = snippet_sentiments[:5]  # Top 5 most emotional
        
        return {
            'sentiment_score': round(overall_sentiment, 3),
            'sentiment_magnitude': round(overall_magnitude, 3),
            'positive_mentions': sentiment_classifications['positive'],
            'negative_mentions': sentiment_classifications['negative'],
            'neutral_mentions': sentiment_classifications['neutral'],
            'total_mentions': len(all_snippets),
            'sample_snippets': sample_snippets,
        }
    
    def batch_analyze(
        self,
        keywords: List[str],
        documents: List[Dict[str, str]]
    ) -> Dict[str, Dict]:
        """
        Analyze sentiment for multiple keywords efficiently.
        
        Args:
            keywords: List of keywords
            documents: List of documents
        
        Returns:
            Dict mapping keyword -> sentiment analysis
        """
        results = {}
        
        for keyword in keywords:
            results[keyword] = self.analyze_keyword_sentiment(
                keyword,
                documents
            )
        
        return results


class AspectBasedSentimentAnalyzer:
    """
    Aspect-based sentiment analysis.
    
    Analyzes sentiment toward specific aspects/entities,
    not just overall document sentiment.
    """
    
    def __init__(self):
        """Initialize aspect-based analyzer."""
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_md")
            except Exception as e:
                logger.warning(f"Failed to load spaCy: {e}")
        
        self.vader = None
        if VADER_AVAILABLE:
            try:
                self.vader = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Failed to load VADER: {e}")
    
    def extract_aspect_opinions(
        self,
        text: str,
        aspect: str
    ) -> List[Tuple[str, float]]:
        """
        Extract opinion words related to an aspect.
        
        Args:
            text: Text to analyze
            aspect: Aspect/keyword to find opinions about
        
        Returns:
            List of (opinion_phrase, sentiment_score) tuples
        """
        if not self.nlp:
            return []
        
        opinions = []
        
        try:
            doc = self.nlp(text)
            aspect_lower = aspect.lower()
            
            # Find sentences containing the aspect
            for sent in doc.sents:
                if aspect_lower in sent.text.lower():
                    # Analyze sentiment of this sentence
                    if self.vader:
                        sentiment = self.vader.polarity_scores(sent.text)['compound']
                    else:
                        sentiment = 0.0
                    
                    opinions.append((sent.text.strip(), sentiment))
        
        except Exception as e:
            logger.warning(f"Aspect opinion extraction failed: {e}")
        
        return opinions
    
    def analyze_aspect_sentiment(
        self,
        aspect: str,
        documents: List[str]
    ) -> Dict[str, any]:
        """
        Analyze sentiment specifically toward an aspect.
        
        Args:
            aspect: The aspect/keyword
            documents: List of document texts
        
        Returns:
            Aspect sentiment analysis
        """
        all_opinions = []
        
        for doc in documents:
            opinions = self.extract_aspect_opinions(doc, aspect)
            all_opinions.extend(opinions)
        
        if not all_opinions:
            return {
                'aspect': aspect,
                'sentiment': 0.0,
                'opinion_count': 0,
                'opinions': []
            }
        
        # Calculate average sentiment
        sentiments = [s for _, s in all_opinions]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Sort by sentiment strength
        all_opinions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return {
            'aspect': aspect,
            'sentiment': round(avg_sentiment, 3),
            'opinion_count': len(all_opinions),
            'opinions': [
                {'text': text, 'sentiment': round(sent, 3)}
                for text, sent in all_opinions[:10]
            ]
        }
