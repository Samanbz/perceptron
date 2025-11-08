"""
Process ALL content from data lake for ALL teams.

This script:
1. Gets ALL unprocessed content from data lake
2. Processes content for EACH team separately
3. Calculates importance for ALL keywords
4. Generates time-series data for each team/day
5. No artificial limits - processes everything

Run this daily or continuously to keep keywords up to date.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.repository import ContentRepository
from keywords import EnhancedKeywordProcessor
from keywords.api_service import KeywordAPIService
from teams.repository import TeamRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_all_content():
    """
    Process ALL content in the data lake for ALL teams.
    
    No limits - processes everything to ensure complete keyword coverage.
    """
    
    print("=" * 80)
    print("PROCESSING ALL CONTENT FOR ALL TEAMS")
    print("=" * 80)
    
    # Initialize repositories
    content_repo = ContentRepository()
    team_repo = TeamRepository()
    
    # Get data lake statistics
    stats = content_repo.get_statistics()
    print(f"\nData Lake Statistics:")
    print(f"  Total documents: {stats['total_content']}")
    print(f"  Processed: {stats['processed']}")
    print(f"  Unprocessed: {stats['unprocessed']}")
    print(f"  By source type: {dict(stats.get('by_source_type', {}))}")
    
    # Get ALL unprocessed content (no limit!)
    print(f"\n[1] Fetching ALL unprocessed content...")
    print("-" * 80)
    unprocessed_content = content_repo.get_unprocessed_content()
    
    if not unprocessed_content:
        print("✓ No unprocessed content found. Everything is up to date!")
        return
    
    print(f"✓ Found {len(unprocessed_content)} unprocessed items")
    
    # Get all active teams
    print(f"\n[2] Getting teams...")
    print("-" * 80)
    teams = [t for t in team_repo.get_all_teams() if t.is_active]
    print(f"✓ Found {len(teams)} active teams:")
    for team in teams:
        print(f"  - {team.team_name} ({team.team_key})")
    
    # Process for each team
    total_keywords_extracted = 0
    total_keywords_stored = 0
    total_importance_calculated = 0
    
    for team in teams:
        print(f"\n[3] Processing content for team: {team.team_name}")
        print("-" * 80)
        
        # Get team sources
        team_sources = [s.source_name for s in team.sources if s.is_enabled]
        print(f"Team monitors {len(team_sources)} sources")
        
        # Filter content for this team's sources
        team_content = [
            c for c in unprocessed_content 
            if c.source_name in team_sources
        ]
        
        if not team_content:
            print(f"  No content from team's sources")
            continue
        
        print(f"  Found {len(team_content)} items from team's sources")
        
        # Initialize processor for this team
        processor = EnhancedKeywordProcessor(team_key=team.team_key)
        
        # Prepare content items
        content_items = [
            {
                'id': content.id,
                'title': content.title,
                'content': content.content,
                'source_type': content.source_type,
                'source_name': content.source_name,
                'published_date': content.published_date,
                'extraction_date': date.today(),
            }
            for content in team_content
        ]
        
        # Process batch (ALL content, no limit)
        print(f"  Processing {len(content_items)} items...")
        result = processor.process_batch(
            content_items=content_items,
            team_key=team.team_key,
            calculate_importance=True,
        )
        
        print(f"  ✓ Batch complete:")
        print(f"    - Successful: {result['successful']}/{result['total']}")
        print(f"    - Keywords extracted: {result['keywords_extracted']}")
        print(f"    - Keywords stored: {result['keywords_stored']}")
        print(f"    - Processing time: {result['processing_time_ms']/1000:.1f}s")
        
        if 'importance_calculation' in result:
            imp = result['importance_calculation']
            print(f"    - Importance calculated: {imp.get('keywords_processed', 0)}")
            print(f"    - Keywords saved: {imp.get('keywords_saved', 0)}")
            total_importance_calculated += imp.get('keywords_saved', 0)
        
        total_keywords_extracted += result['keywords_extracted']
        total_keywords_stored += result['keywords_stored']
        
        # Generate time-series for last 30 days
        print(f"  Generating time-series data...")
        ts_result = processor.generate_timeseries(
            team_key=team.team_key,
            days=30,
        )
        print(f"  ✓ Time-series: {ts_result['timeseries_created']} data points created")
        
        # Mark content as processed
        for content in team_content:
            content_repo.mark_as_processed(content.id, status='completed')
        
        processor.close()
    
    # Summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nTotal Results:")
    print(f"  Documents processed: {len(unprocessed_content)}")
    print(f"  Teams processed: {len(teams)}")
    print(f"  Keywords extracted: {total_keywords_extracted}")
    print(f"  Keywords stored: {total_keywords_stored}")
    print(f"  Importance calculated: {total_importance_calculated}")
    
    content_repo.close()
    team_repo.close()
    
    print("\n✓ All content processed and ready for frontend!")


def process_specific_date(target_date: date):
    """
    Reprocess content for a specific date.
    
    Useful for:
    - Fixing missing data
    - Recomputing with new algorithms
    - Backfilling historical data
    """
    
    print("=" * 80)
    print(f"REPROCESSING CONTENT FOR {target_date}")
    print("=" * 80)
    
    content_repo = ContentRepository()
    team_repo = TeamRepository()
    
    # Get content for specific date
    next_day = target_date + timedelta(days=1)
    content_items = content_repo.get_content_by_date_range(
        start_date=target_date,
        end_date=next_day
    )
    
    print(f"\n✓ Found {len(content_items)} items for {target_date}")
    
    if not content_items:
        print("No content found for this date")
        return
    
    # Process for each team
    teams = [t for t in team_repo.get_all_teams() if t.is_active]
    
    for team in teams:
        print(f"\nProcessing for team: {team.team_name}")
        
        team_sources = [s.source_name for s in team.sources if s.is_enabled]
        team_content = [
            c for c in content_items 
            if c.source_name in team_sources
        ]
        
        if not team_content:
            continue
        
        print(f"  {len(team_content)} items from team's sources")
        
        processor = EnhancedKeywordProcessor(team_key=team.team_key)
        
        items = [
            {
                'id': c.id,
                'title': c.title,
                'content': c.content,
                'source_type': c.source_type,
                'source_name': c.source_name,
                'published_date': c.published_date,
                'extraction_date': target_date,
            }
            for c in team_content
        ]
        
        result = processor.process_batch(
            content_items=items,
            team_key=team.team_key,
            calculate_importance=True,
        )
        
        print(f"  ✓ {result['keywords_stored']} keywords stored")
        
        processor.close()
    
    content_repo.close()
    team_repo.close()
    
    print("\n✓ Reprocessing complete!")


def show_daily_keywords(team_key: str, target_date: date = None, limit: int = 20):
    """
    Show top keywords for a team on a specific date.
    
    This is what the frontend will call via API.
    """
    
    if target_date is None:
        target_date = date.today()
    
    print("=" * 80)
    print(f"TOP KEYWORDS: {team_key.upper()} - {target_date}")
    print("=" * 80)
    
    api_service = KeywordAPIService()
    
    # Get word cloud data (this is what frontend receives)
    word_cloud = api_service.get_word_cloud_data(
        team_key=team_key,
        target_date=target_date,
        limit=limit,  # Only limit for frontend display
        min_importance=30.0,
    )
    
    print(f"\nTeam: {word_cloud.team_name}")
    print(f"Date Range: {word_cloud.date_range['start']} to {word_cloud.date_range['end']}")
    print(f"Total Keywords: {word_cloud.total_keywords}")
    print(f"Total Documents: {word_cloud.total_documents}")
    
    if word_cloud.keywords:
        print(f"\nTop {len(word_cloud.keywords)} Keywords:")
        print(f"{'Rank':<6} {'Keyword':<25} {'Importance':<12} {'Freq':<6} {'Sentiment'}")
        print("-" * 80)
        
        for i, kw in enumerate(word_cloud.keywords, 1):
            sentiment_str = f"{kw.sentiment.score:+.2f}"
            print(
                f"{i:<6} {kw.keyword[:24]:<25} "
                f"{kw.importance:<12.1f} {kw.metrics.frequency:<6} {sentiment_str}"
            )
    else:
        print("\nNo keywords found for this date")
    
    api_service.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process content for all teams")
    parser.add_argument(
        'command',
        choices=['process', 'reprocess', 'show'],
        help='Command to run'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date in YYYY-MM-DD format (for reprocess/show)'
    )
    parser.add_argument(
        '--team',
        type=str,
        default='regulator',
        help='Team key (for show command)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Number of keywords to show (for show command)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'process':
        process_all_content()
    
    elif args.command == 'reprocess':
        if not args.date:
            print("Error: --date required for reprocess")
            sys.exit(1)
        target_date = date.fromisoformat(args.date)
        process_specific_date(target_date)
    
    elif args.command == 'show':
        target_date = date.fromisoformat(args.date) if args.date else date.today()
        show_daily_keywords(args.team, target_date, args.limit)
