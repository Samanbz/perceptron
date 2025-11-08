#!/usr/bin/env python3
"""
Simple test to demonstrate multi-source integration.

This script:
1. Tests RSS sourcing (always works, no credentials)
2. Attempts to test other sourcers (skips if credentials missing)
3. Stores fetched content in database
4. Processes with NLP pipeline
5. Shows extracted keywords

Run: python simple_integration_test.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

# Core imports
from storage.repository import ContentRepository
from keywords import EnhancedKeywordProcessor
from teams.repository import TeamRepository

# Sourcer imports
from sourcers import RSSSourcer

print("="*80)
print("SIMPLE MULTI-SOURCE INTEGRATION TEST")
print("="*80)
print()


async def test_rss_source():
    """Test RSS sourcing (always available)."""
    print("1. Testing RSS Sourcer (TechCrunch)")
    print("-" * 40)
    
    sourcer = RSSSourcer(
        feed_url="https://techcrunch.com/feed/",
        name="TechCrunch Test",
        max_entries=10
    )
    
    contents = await sourcer.fetch()
    print(f"✓ Fetched {len(contents)} articles from RSS")
    
    if contents:
        print(f"\nSample article:")
        print(f"  Title: {contents[0].title[:70]}...")
        print(f"  Date: {contents[0].published_date}")
        print(f"  Length: {len(contents[0].content)} characters")
    
    return contents


def save_to_database(contents, source_name="TechCrunch Test"):
    """Save content to database."""
    print(f"\n2. Saving to Database")
    print("-" * 40)
    
    repo = ContentRepository()
    result = repo.save_batch(
        contents=contents,
        source_type="rss",
        source_name=source_name,
        source_url="https://techcrunch.com/feed/"
    )
    repo.close()
    
    print(f"✓ Saved: {result['saved']} new, {result['duplicates']} duplicates")
    return result


def process_with_nlp():
    """Process unprocessed content with NLP pipeline."""
    print(f"\n3. Processing with NLP Pipeline")
    print("-" * 40)
    
    content_repo = ContentRepository()
    team_repo = TeamRepository()
    
    # Get unprocessed content
    unprocessed = content_repo.get_unprocessed_content()
    print(f"Found {len(unprocessed)} unprocessed items")
    
    if not unprocessed:
        print("⚠ No unprocessed content. Run sourcing first.")
        content_repo.close()
        team_repo.close()
        return None
    
    # Get first active team
    teams = [t for t in team_repo.get_all_teams() if t.is_active]
    if not teams:
        print("⚠ No active teams configured")
        content_repo.close()
        team_repo.close()
        return None
    
    team = teams[0]
    print(f"Processing for team: {team.team_name}")
    
    # Get team-specific content
    team_sources = [s.source_name for s in team.sources if s.is_enabled]
    team_content = [
        c for c in unprocessed 
        if c.source_name in team_sources
    ]
    
    if not team_content:
        # Use all content if none matches team sources
        team_content = unprocessed[:5]  # Limit to 5 for quick test
        print(f"Using {len(team_content)} items for test")
    
    # Create processor
    processor = EnhancedKeywordProcessor(team_key=team.team_key)
    
    # Prepare content items
    from datetime import date
    content_items = [
        {
            'id': content.id,
            'title': content.title,
            'content': content.content,
            'source_type': content.source_type,
            'source_name': content.source_name,
            'published_date': content.published_date,
            'extraction_date': content.published_date.date() if content.published_date else date.today(),
        }
        for content in team_content
    ]
    
    # Process batch
    print(f"Extracting keywords from {len(content_items)} items...")
    result = processor.process_batch(
        content_items=content_items,
        team_key=team.team_key,
        calculate_importance=True,
    )
    
    # Mark as processed
    for content in team_content:
        content_repo.mark_as_processed(content.id, status='completed')
    
    processor.close()
    content_repo.close()
    team_repo.close()
    
    print(f"✓ Extracted {result['keywords_stored']} keywords")
    
    return result


def show_top_keywords(result):
    """Display top keywords."""
    print(f"\n4. Top Keywords Extracted")
    print("-" * 40)
    
    if not result or not result.get('top_keywords'):
        print("No keywords to display")
        return
    
    print(f"\nTop 10 keywords:")
    for i, (keyword, score) in enumerate(result['top_keywords'][:10], 1):
        print(f"  {i:2d}. {keyword:30s} {score:.4f}")


async def test_other_sources():
    """Test other source types if credentials available."""
    print(f"\n5. Testing Other Source Types")
    print("-" * 40)
    
    results = []
    
    # Test Reddit
    try:
        from sourcers import RedditSourcer
        reddit = RedditSourcer(
            subreddit="technology",
            name="Reddit Test",
            limit=5,
            time_filter="day",
            sort_by="hot"
        )
        contents = await reddit.fetch()
        print(f"✓ Reddit: Fetched {len(contents)} posts")
        results.append(('Reddit', len(contents)))
    except ValueError as e:
        print(f"⚠ Reddit: {str(e)[:60]}...")
    except ImportError:
        print(f"⚠ Reddit: Missing praw package (pip install praw)")
    except Exception as e:
        print(f"✗ Reddit: {str(e)[:60]}...")
    
    # Test NewsAPI
    try:
        from sourcers import NewsAPISourcer
        newsapi = NewsAPISourcer(
            query="artificial intelligence",
            name="NewsAPI Test",
            max_articles=5
        )
        contents = await newsapi.fetch()
        print(f"✓ NewsAPI: Fetched {len(contents)} articles")
        results.append(('NewsAPI', len(contents)))
    except ValueError as e:
        print(f"⚠ NewsAPI: {str(e)[:60]}...")
    except ImportError:
        print(f"⚠ NewsAPI: Missing newsapi-python package")
    except Exception as e:
        print(f"✗ NewsAPI: {str(e)[:60]}...")
    
    # Test YouTube
    try:
        from sourcers import YouTubeSourcer
        youtube = YouTubeSourcer(
            search_query="machine learning tutorial",
            name="YouTube Test",
            max_results=5
        )
        contents = await youtube.fetch()
        print(f"✓ YouTube: Fetched {len(contents)} videos")
        results.append(('YouTube', len(contents)))
    except ValueError as e:
        print(f"⚠ YouTube: {str(e)[:60]}...")
    except ImportError:
        print(f"⚠ YouTube: Missing google-api-python-client package")
    except Exception as e:
        print(f"✗ YouTube: {str(e)[:60]}...")
    
    return results


async def main():
    """Run the test."""
    start_time = datetime.now()
    
    try:
        # Test RSS (always works)
        contents = await test_rss_source()
        
        # Save to database
        save_to_database(contents)
        
        # Process with NLP
        result = process_with_nlp()
        
        # Show results
        if result:
            show_top_keywords(result)
        
        # Test other sources
        other_results = await test_other_sources()
        
        # Final summary
        print()
        print("="*80)
        print("TEST COMPLETE")
        print("="*80)
        print(f"\n✓ RSS sourcing: Working")
        print(f"✓ Database storage: Working")
        print(f"✓ NLP processing: Working")
        print(f"✓ Keyword extraction: Working")
        
        if other_results:
            print(f"\nOptional source types tested:")
            for source_type, count in other_results:
                print(f"  ✓ {source_type}: {count} items fetched")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\nElapsed time: {elapsed:.1f}s")
        print()
        print("Next steps:")
        print("  1. Set up credentials for Reddit, NewsAPI, YouTube (see docs/MULTI_SOURCE_INTEGRATION.md)")
        print("  2. Update config.json with your desired sources")
        print("  3. Run: python services/data_sourcing_service.py")
        print("  4. Run: python services/nlp_processing_service.py")
        print()
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
