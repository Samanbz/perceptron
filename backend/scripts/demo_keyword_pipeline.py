#!/usr/bin/env python3
"""
Demonstrator for the Document → Keywords pipeline.

Shows the complete flow from fetching content to extracting keywords
with detailed output and statistics.

Usage:
    python demo_keyword_pipeline.py              # Demo with 5 articles
    python demo_keyword_pipeline.py 10           # Demo with 10 articles
    python demo_keyword_pipeline.py --full       # Process all unprocessed content
"""

import sys
import os
from datetime import datetime, date
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from storage.repository import ContentRepository
from storage.models import SourcedContentModel
from keywords.processor import RealtimeKeywordProcessor
from keywords.repository import KeywordRepository, KeywordConfigRepository


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    print("\n" + char * 80)
    print(f"  {text}")
    print(char * 80 + "\n")


def print_section(text: str):
    """Print a section divider."""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print(f"{'─' * 80}\n")


def demonstrate_pipeline(limit: int = 5, process_all: bool = False):
    """
    Demonstrate the complete document → keywords pipeline.
    
    Args:
        limit: Number of documents to process
        process_all: Process all unprocessed content if True
    """
    start_time = datetime.now()
    
    print_header("📄 DOCUMENT → KEYWORDS PIPELINE DEMO", "=")
    
    # Step 1: Check current state
    print_section("STEP 1: Checking Database Status")
    
    content_repo = ContentRepository()
    keyword_repo = KeywordRepository()
    config_repo = KeywordConfigRepository()
    
    # Get content stats
    total_content = content_repo.session.query(SourcedContentModel).count()
    unprocessed = content_repo.session.query(SourcedContentModel).filter(
        SourcedContentModel.processed == 0
    ).count()
    
    print(f"📊 Content Database:")
    print(f"   Total articles: {total_content}")
    print(f"   Unprocessed: {unprocessed}")
    
    # Get keyword stats
    kw_stats = keyword_repo.get_statistics()
    print(f"\n🔑 Keyword Database:")
    print(f"   Total keyword records: {kw_stats['total_keywords']}")
    print(f"   Unique keywords: {kw_stats['unique_keywords']}")
    print(f"   Today's extractions: {kw_stats['today']}")
    
    # Get active config
    active_config = config_repo.get_active_config()
    if active_config:
        print(f"\n⚙️  Active Configuration: {active_config.config_name}")
        print(f"   Relevance threshold: {active_config.relevance_threshold}")
        print(f"   Weights: TF-IDF={active_config.tfidf_weight}, "
              f"spaCy={active_config.spacy_weight}, YAKE={active_config.yake_weight}")
        print(f"   Max keywords/source: {active_config.max_keywords_per_source}")
    else:
        print("\n⚠️  No active configuration found!")
        return
    
    # Step 2: Get content to process
    print_section("STEP 2: Fetching Content to Process")
    
    if process_all:
        content_items = content_repo.session.query(SourcedContentModel).all()
        print(f"📥 Processing ALL content ({len(content_items)} items)")
    else:
        # Try unprocessed first
        content_items = content_repo.get_unprocessed_content(limit=limit)
        
        if not content_items:
            print("   No unprocessed content. Using recent content instead...")
            content_items = content_repo.session.query(SourcedContentModel).limit(limit).all()
        
        print(f"📥 Selected {len(content_items)} articles for processing")
    
    if not content_items:
        print("\n❌ No content found in database!")
        print("\n💡 Run: python setup_data_lake.py fetch")
        return
    
    # Show what we're processing
    print("\nContent to process:")
    for i, item in enumerate(content_items, 1):
        print(f"   {i}. [{item.source_name}] {item.title[:60]}...")
    
    # Step 3: Extract keywords
    print_section("STEP 3: Extracting Keywords (Real-Time Processing)")
    
    processor = RealtimeKeywordProcessor()
    results = []
    
    for i, item in enumerate(content_items, 1):
        print(f"\n[{i}/{len(content_items)}] Processing: {item.title[:70]}...")
        print(f"      Source: {item.source_name} ({item.source_type})")
        print(f"      Content length: {len(item.content)} chars")
        
        # Extract keywords
        result = processor.process_content(
            content_id=item.id,
            title=item.title,
            content=item.content,
            source_type=item.source_type,
            source_name=item.source_name,
        )
        
        results.append(result)
        
        # Show results
        if result['status'] == 'success':
            print(f"      ✓ Extracted: {result['keywords_extracted']} keywords")
            print(f"      ✓ Stored: {result['keywords_stored']} keywords "
                  f"(threshold={result['relevance_threshold']:.2f})")
            print(f"      ✓ Time: {result['processing_time_ms']:.1f}ms")
        else:
            print(f"      ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Step 4: Show extracted keywords
    print_section("STEP 4: Showing Extracted Keywords")
    
    # Refresh stats
    kw_stats = keyword_repo.get_statistics()
    
    print(f"📊 Updated Statistics:")
    print(f"   Total keyword records: {kw_stats['total_keywords']}")
    print(f"   Unique keywords: {kw_stats['unique_keywords']}")
    print(f"   Today's extractions: {kw_stats['today']}")
    
    if kw_stats['by_source']:
        print(f"\n   By source:")
        for source, count in sorted(kw_stats['by_source'].items(), key=lambda x: x[1], reverse=True):
            print(f"      {source}: {count}")
    
    # Show today's top keywords
    print(f"\n🔝 Top Keywords from Today (threshold={active_config.relevance_threshold}):")
    
    today_keywords = keyword_repo.get_daily_keywords(
        extraction_date=date.today(),
        min_relevance=active_config.relevance_threshold,
        limit=30
    )
    
    if today_keywords:
        for i, kw in enumerate(today_keywords[:20], 1):
            type_icon = {
                'entity': '👤',
                'phrase': '📝',
                'single': '🔤'
            }.get(kw.keyword_type, '•')
            
            entity_info = f" ({kw.entity_type})" if kw.entity_type else ""
            
            print(f"   {i:2d}. {type_icon} {kw.keyword:40s} "
                  f"score={kw.relevance_score:.3f}{entity_info}")
    else:
        print("   No keywords found above threshold.")
        print(f"\n   💡 Try lowering the threshold:")
        print(f"      python setup_keywords.py demo")
        print(f"      python setup_keywords.py activate demo")
    
    # Step 5: Processing summary
    print_section("STEP 5: Processing Summary")
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    total_extracted = sum(r.get('keywords_extracted', 0) for r in results)
    total_stored = sum(r.get('keywords_stored', 0) for r in results)
    total_time = sum(r.get('processing_time_ms', 0) for r in results)
    
    print(f"📈 Batch Results:")
    print(f"   Documents processed: {len(results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total keywords extracted: {total_extracted}")
    print(f"   Total keywords stored: {total_stored}")
    print(f"   Total processing time: {total_time:.1f}ms")
    print(f"   Average time per doc: {total_time/len(results):.1f}ms")
    
    if total_extracted > 0:
        storage_rate = (total_stored / total_extracted) * 100
        print(f"   Storage rate: {storage_rate:.1f}% (based on threshold)")
    
    # Step 6: Show trending keywords
    print_section("STEP 6: Trending Keywords (Last 7 Days)")
    
    trending = keyword_repo.get_top_keywords(
        days=7,
        min_relevance=active_config.relevance_threshold,
        limit=15
    )
    
    if trending:
        print("🔥 Most relevant keywords across all sources:\n")
        for i, kw in enumerate(trending, 1):
            print(f"   {i:2d}. {kw['keyword']:40s} "
                  f"score={kw['max_relevance']:.3f}  "
                  f"freq={kw['total_frequency']:3d}  "
                  f"docs={kw['appearance_count']:2d}")
    else:
        print("   No trending keywords found.")
    
    # Cleanup
    processor.close()
    keyword_repo.close()
    config_repo.close()
    content_repo.close()
    
    # Final summary
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print_header("✅ DEMO COMPLETE!", "=")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Documents processed: {len(results)}")
    print(f"Keywords stored: {total_stored}")
    print(f"\n💡 Next steps:")
    print(f"   - View stats: python setup_keywords.py stats")
    print(f"   - Fetch more content: python setup_data_lake.py fetch")
    print(f"   - Adjust threshold: python setup_keywords.py activate <config>")
    print()


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--full':
            demonstrate_pipeline(process_all=True)
        else:
            try:
                limit = int(sys.argv[1])
                demonstrate_pipeline(limit=limit)
            except ValueError:
                print("Usage: python demo_keyword_pipeline.py [number|--full]")
                sys.exit(1)
    else:
        demonstrate_pipeline(limit=5)


if __name__ == "__main__":
    main()
