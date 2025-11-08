"""
Reprocess all documents and assign keywords to their document published dates.

This script:
1. Groups documents by their published date
2. Filters documents by team-specific sources
3. Processes each date group separately per team
4. Assigns keywords to the published date instead of today
"""

import sys
import logging
import json
from datetime import datetime, date, timedelta
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, '/Users/samanb/dev/perceptron/backend')

from keywords.enhanced_processor import EnhancedKeywordProcessor
from storage.repository import ContentRepository
from teams.repository import TeamRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_team_sources():
    """Load team-specific source configuration from config.json"""
    config_path = Path(__file__).parent.parent / 'config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Build mapping of team_key -> list of source names
    team_sources = {}
    for team in config['teams']:
        team_key = team['team_key']
        sources = []
        for source in team.get('sources', []):
            # Normalize source name for matching
            source_name = source['source_name']
            sources.append(source_name.lower())
        team_sources[team_key] = sources
    
    return team_sources


def reprocess_all_with_published_dates():
    """Reprocess all content with proper published date assignment and team-specific filtering."""
    
    logger.info("=" * 80)
    logger.info("REPROCESSING ALL DOCUMENTS BY PUBLISHED DATE (TEAM-FILTERED)")
    logger.info("=" * 80)
    
    # Load team-specific sources
    team_sources = load_team_sources()
    logger.info(f"Loaded source configuration for {len(team_sources)} teams")
    for team_key, sources in team_sources.items():
        logger.info(f"  {team_key}: {len(sources)} configured sources")
    
    # Initialize repositories
    content_repo = ContentRepository()
    team_repo = TeamRepository()
    
    # Get all teams
    teams = team_repo.get_all_teams()
    logger.info(f"Processing for {len(teams)} teams: {[t.team_key for t in teams]}")
    
    # Get date range (last 7 days)
    today = date.today()
    start_date = today - timedelta(days=6)
    
    logger.info(f"Date range: {start_date} to {today}")
    
    # Get all documents in date range
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())
    
    all_documents = content_repo.get_content_by_date_range(start_dt, end_dt)
    logger.info(f"Found {len(all_documents)} total documents")
    
    # Group documents by published date
    docs_by_date = defaultdict(list)
    for doc in all_documents:
        if doc.published_date:
            pub_date = doc.published_date.date()
            docs_by_date[pub_date].append(doc)
    
    logger.info(f"Documents grouped into {len(docs_by_date)} dates")
    for date_key in sorted(docs_by_date.keys()):
        logger.info(f"  {date_key}: {len(docs_by_date[date_key])} documents")
    
    # Process each team
    total_keywords_saved = 0
    
    for team in teams:
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing team: {team.team_name} ({team.team_key})")
        logger.info(f"{'='*80}")
        
        # Get configured sources for this team
        team_source_names = team_sources.get(team.team_key, [])
        if not team_source_names:
            logger.warning(f"  No sources configured for team {team.team_key}, skipping")
            continue
        
        logger.info(f"  Filtering for {len(team_source_names)} team sources")
        
        processor = EnhancedKeywordProcessor(team_key=team.team_key)
        
        # Process each date separately
        for pub_date in sorted(docs_by_date.keys()):
            all_docs_for_date = docs_by_date[pub_date]
            
            # Filter documents by team-specific sources
            team_documents = []
            for doc in all_docs_for_date:
                doc_source_name = (doc.source_name or '').lower()
                # Check if this document's source matches any of the team's configured sources
                if any(team_src in doc_source_name for team_src in team_source_names):
                    team_documents.append(doc)
            
            if not team_documents:
                logger.info(f"\nProcessing {pub_date}: 0 documents for {team.team_key} (filtered from {len(all_docs_for_date)})")
                continue
            
            logger.info(f"\nProcessing {pub_date}: {len(team_documents)} documents for {team.team_key} (filtered from {len(all_docs_for_date)})")
            
            # Convert to format expected by processor
            content_items = []
            for doc in team_documents:
                content_items.append({
                    'id': doc.id,
                    'title': doc.title or '',
                    'content': doc.content or '',
                    'source_type': doc.source_type,
                    'source_name': doc.source_name,
                    'published_date': doc.published_date.date() if doc.published_date else None,
                    'extraction_date': pub_date,  # Use published date for extraction
                })
            
            # Process batch
            result = processor.process_batch(
                content_items=content_items,
                team_key=team.team_key,
                calculate_importance=False,  # Don't calculate yet
            )
            
            logger.info(
                f"  Extracted: {result['successful']} successful, "
                f"{result['keywords_extracted']} keywords"
            )
            
            # Now calculate importance with the published date
            importance_result = processor.calculate_importance_and_sentiment(
                analysis_date=pub_date,  # KEY: Use published date
                team_key=team.team_key,
            )
            
            keywords_saved = importance_result.get('keywords_saved', 0)
            total_keywords_saved += keywords_saved
            
            logger.info(
                f"  Importance calculated: {importance_result['keywords_processed']} processed, "
                f"{keywords_saved} saved"
            )
    
    logger.info(f"\n{'='*80}")
    logger.info(f"REPROCESSING COMPLETE")
    logger.info(f"Total keywords saved across all teams/dates: {total_keywords_saved}")
    logger.info(f"{'='*80}")


if __name__ == '__main__':
    try:
        reprocess_all_with_published_dates()
    except Exception as e:
        logger.error(f"Reprocessing failed: {e}", exc_info=True)
        sys.exit(1)
