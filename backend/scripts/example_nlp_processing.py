"""
Example: Processing stored content for NLP/ML tasks.

This demonstrates how to:
1. Retrieve unprocessed content from the data lake
2. Perform TF-IDF analysis
3. Extract keywords
4. Mark content as processed
"""

from datetime import datetime, timedelta
from collections import Counter
import re

from storage import ContentRepository


def clean_text(text: str) -> str:
    """Clean text for processing."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.lower()


def extract_keywords(text: str, top_n: int = 10) -> list:
    """
    Simple keyword extraction (word frequency).
    
    In production, use TF-IDF or more sophisticated methods.
    """
    # Clean text
    text = clean_text(text)
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'that',
        'this', 'these', 'those', 'it', 'its', 'they', 'their', 'them',
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]{3,}\b', text)
    
    # Filter stop words
    words = [w for w in words if w not in stop_words]
    
    # Count frequency
    counter = Counter(words)
    
    # Return top keywords
    return [word for word, count in counter.most_common(top_n)]


def simple_sentiment(text: str) -> dict:
    """
    Very simple sentiment analysis (word counting).
    
    In production, use TextBlob, VADER, or transformer models.
    """
    text = text.lower()
    
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'positive', 'success', 'successful', 'win', 'winning', 'growth',
        'improve', 'innovation', 'innovative', 'breakthrough', 'achievement',
    }
    
    negative_words = {
        'bad', 'terrible', 'awful', 'poor', 'negative', 'failure', 'failed',
        'lose', 'losing', 'decline', 'crisis', 'problem', 'issue', 'concern',
        'risk', 'threat', 'challenge', 'difficult', 'struggle',
    }
    
    words = set(re.findall(r'\b[a-z]+\b', text))
    
    positive_count = len(words & positive_words)
    negative_count = len(words & negative_words)
    
    total = positive_count + negative_count
    if total == 0:
        sentiment = 'neutral'
        score = 0.0
    elif positive_count > negative_count:
        sentiment = 'positive'
        score = (positive_count - negative_count) / total
    elif negative_count > positive_count:
        sentiment = 'negative'
        score = (negative_count - positive_count) / total * -1
    else:
        sentiment = 'neutral'
        score = 0.0
    
    return {
        'sentiment': sentiment,
        'score': score,
        'positive_words': positive_count,
        'negative_words': negative_count,
    }


def process_batch():
    """Process a batch of unprocessed content."""
    print("=" * 70)
    print("NLP Processing Example")
    print("=" * 70)
    
    repo = ContentRepository()
    
    # Get unprocessed content
    batch_size = 20
    items = repo.get_unprocessed_content(limit=batch_size)
    
    if not items:
        print("\nNo unprocessed content found!")
        print("Run: python setup_data_lake.py fetch")
        return
    
    print(f"\nProcessing {len(items)} items...\n")
    
    for i, item in enumerate(items, 1):
        print(f"{i}. {item.title[:60]}...")
        
        # Extract keywords
        keywords = extract_keywords(item.content, top_n=5)
        print(f"   Keywords: {', '.join(keywords)}")
        
        # Sentiment analysis
        sentiment = simple_sentiment(item.content)
        print(f"   Sentiment: {sentiment['sentiment']} (score: {sentiment['score']:.2f})")
        
        # Word count
        word_count = len(item.content.split())
        print(f"   Words: {word_count}")
        
        # Store analysis results (in production, save to separate table)
        # For now, just mark as processed
        repo.mark_as_processed(item.id, status='completed')
        print(f"   ✓ Marked as processed\n")
    
    repo.close()
    
    print("=" * 70)
    print(f"Processed {len(items)} items successfully!")
    print("=" * 70)


def analyze_trends():
    """Analyze trends over time."""
    print("\n" + "=" * 70)
    print("Trend Analysis")
    print("=" * 70)
    
    repo = ContentRepository()
    
    # Get content from last 24 hours
    start_date = datetime.now() - timedelta(hours=24)
    items = repo.get_content_by_date_range(start_date)
    
    if not items:
        print("\nNo content found in last 24 hours!")
        return
    
    print(f"\nAnalyzing {len(items)} items from last 24 hours...\n")
    
    # Aggregate keywords
    all_keywords = []
    sentiments = []
    
    for item in items:
        keywords = extract_keywords(item.content, top_n=10)
        all_keywords.extend(keywords)
        
        sentiment = simple_sentiment(item.content)
        sentiments.append(sentiment)
    
    # Top trending keywords
    keyword_counts = Counter(all_keywords)
    print("Top Trending Keywords:")
    for keyword, count in keyword_counts.most_common(10):
        print(f"  {keyword}: {count}")
    
    # Overall sentiment
    print("\nSentiment Distribution:")
    sentiment_dist = Counter(s['sentiment'] for s in sentiments)
    for sentiment, count in sentiment_dist.items():
        percentage = (count / len(sentiments)) * 100
        print(f"  {sentiment}: {count} ({percentage:.1f}%)")
    
    # Average sentiment score
    avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
    print(f"\nAverage Sentiment Score: {avg_score:.3f}")
    
    repo.close()
    
    print("\n" + "=" * 70)


def source_comparison():
    """Compare content across different sources."""
    print("\n" + "=" * 70)
    print("Source Comparison")
    print("=" * 70)
    
    repo = ContentRepository()
    
    stats = repo.get_statistics()
    
    print(f"\nTotal Content: {stats['total_content']}")
    print(f"Processed: {stats['processed']}")
    print(f"Unprocessed: {stats['unprocessed']}")
    
    print("\nContent by Source Type:")
    for source_type, count in stats['by_source_type'].items():
        print(f"  {source_type}: {count}")
    
    # Get recent items by source
    start_date = datetime.now() - timedelta(days=7)
    items = repo.get_content_by_date_range(start_date)
    
    # Group by source name
    by_source = {}
    for item in items:
        if item.source_name not in by_source:
            by_source[item.source_name] = []
        by_source[item.source_name].append(item)
    
    print(f"\nContent by Source (last 7 days):")
    for source_name, items in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {source_name}: {len(items)} articles")
    
    repo.close()
    
    print("\n" + "=" * 70)


def main():
    """Run all examples."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process":
            process_batch()
        elif command == "trends":
            analyze_trends()
        elif command == "compare":
            source_comparison()
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        # Run all
        process_batch()
        analyze_trends()
        source_comparison()


def print_usage():
    """Print usage instructions."""
    print("""
Usage: python example_nlp_processing.py [command]

Commands:
  process   - Process batch of unprocessed content
  trends    - Analyze trending keywords and sentiment
  compare   - Compare content across sources
  
  (no command) - Run all examples
    """)


if __name__ == "__main__":
    main()
