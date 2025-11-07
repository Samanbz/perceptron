#!/usr/bin/env python3
"""
Test keyword extraction on existing content.

Usage:
    python test_keyword_extraction.py         # Process 5 items
    python test_keyword_extraction.py 20      # Process 20 items
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage.repository import ContentRepository
from keywords.processor import RealtimeKeywordProcessor
from keywords.repository import KeywordRepository


def test_extraction(limit: int = 5):
    """Test keyword extraction on existing content."""
    
    # Get unprocessed content
    content_repo = ContentRepository()
    content_items = content_repo.get_unprocessed_content(limit=limit)
    
    if not content_items:
        print("No unprocessed content found. Trying processed content...")
        all_content = content_repo.session.query(content_repo.model).limit(limit).all()
        content_items = all_content
    
    if not content_items:
        print("No content found in database!")
        return
    
    print(f"\n=== Testing Keyword Extraction on {len(content_items)} items ===\n")
    
    # Initialize processor
    processor = RealtimeKeywordProcessor()
    
    # Process each item
    for item in content_items:
        print(f"\nProcessing: {item.title[:70]}...")
        print(f"Source: {item.source_name} ({item.source_type})")
        
        result = processor.process_content(
            content_id=item.id,
            title=item.title,
            content=item.content,
            source_type=item.source_type,
            source_name=item.source_name,
        )
        
        if result['status'] == 'success':
            print(f"✓ Extracted {result['keywords_extracted']} keywords")
            print(f"✓ Stored {result['keywords_stored']} keywords (threshold={result['relevance_threshold']:.2f})")
            print(f"✓ Processing time: {result['processing_time_ms']:.1f}ms")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Show statistics
    print("\n" + "="*70)
    print("=== Keyword Database Statistics ===")
    print("="*70 + "\n")
    
    keyword_repo = KeywordRepository()
    stats = keyword_repo.get_statistics()
    
    print(f"Total keyword records: {stats['total_keywords']}")
    print(f"Unique keywords: {stats['unique_keywords']}")
    print(f"Today's extractions: {stats['today']}")
    
    if stats['by_source']:
        print("\nBy source:")
        for source, count in stats['by_source'].items():
            print(f"  {source}: {count}")
    
    # Show top keywords
    print("\n" + "="*70)
    print("=== Top Keywords (last 7 days, min relevance 0.7) ===")
    print("="*70 + "\n")
    
    top = keyword_repo.get_top_keywords(days=7, min_relevance=0.7, limit=30)
    
    if top:
        for i, kw in enumerate(top, 1):
            print(
                f"{i:2d}. {kw['keyword']:35s} "
                f"score={kw['max_relevance']:.3f} "
                f"freq={kw['total_frequency']:3d}"
            )
    else:
        print("No keywords found")
    
    # Cleanup
    processor.close()
    keyword_repo.close()
    content_repo.close()
    
    print("\n✓ Test complete!\n")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    test_extraction(limit)
