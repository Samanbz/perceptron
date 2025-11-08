#!/usr/bin/env python3
"""
Fetch all documents from all sources and process keywords.
Runs in foreground with verbose logging.
"""

import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sourcers.rss_sourcer import RSSSourcer
from storage.repository import ContentRepository
from storage.models import get_session
from keywords.enhanced_processor import EnhancedKeywordProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


async def fetch_from_source(source_config: dict, team_key: str, team_name: str):
    """Fetch documents from a single source."""
    source_type = source_config["source_type"]
    source_name = source_config["source_name"]
    source_url = source_config["source_url"]
    config = source_config.get("config", {})
    
    logger.info(f"Fetching from: {source_name} ({team_name})")
    
    try:
        if source_type == "rss":
            max_entries = config.get("max_entries", 500)
            sourcer = RSSSourcer(feed_url=source_url, max_entries=max_entries)
            items = await sourcer.fetch()
        else:
            logger.warning(f"Skipping unsupported source type: {source_type}")
            return []
        
        if not items:
            logger.warning(f"No items fetched from {source_name}")
            return []
        
        logger.info(f"✓ Fetched {len(items)} items from {source_name}")
        
        # Save to database
        session = get_session()
        repo = ContentRepository(session)
        saved_count = 0
        duplicate_count = 0
        
        for item in items:
            _, is_new = repo.save_content(
                content=item,
                source_type=source_type,
                source_name=source_name,
                source_url=source_url
            )
            if is_new:
                saved_count += 1
            else:
                duplicate_count += 1
        
        session.commit()
        session.close()
        
        logger.info(f"✓ Saved {saved_count} new documents, {duplicate_count} duplicates from {source_name}")
        return items
        
    except Exception as e:
        logger.error(f"✗ Error fetching from {source_name}: {str(e)}")
        return []


async def fetch_all_sources():
    """Fetch from all sources in config."""
    config = load_config()
    
    total_fetched = 0
    total_saved = 0
    
    for team in config["teams"]:
        if not team.get("is_active", True):
            continue
        
        team_key = team["team_key"]
        team_name = team["team_name"]
        
        logger.info(f"\n{'='*80}")
        logger.info(f"PROCESSING TEAM: {team_name}")
        logger.info(f"{'='*80}")
        
        for source in team["sources"]:
            items = await fetch_from_source(source, team_key, team_name)
            total_fetched += len(items)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"FETCH COMPLETE")
    logger.info(f"Total items fetched: {total_fetched}")
    logger.info(f"{'='*80}\n")


def process_keywords():
    """Process keywords for all documents."""
    logger.info(f"\n{'='*80}")
    logger.info("STARTING KEYWORD PROCESSING")
    logger.info(f"{'='*80}\n")
    
    # Load config for team information
    config = load_config()
    teams = {team["team_key"]: team for team in config["teams"] if team.get("is_active", True)}
    
    # Get documents from last 7 days
    session = get_session()
    repo = ContentRepository(session)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    logger.info(f"Processing documents from {start_date.date()} to {end_date.date()}")
    
    # Process each team
    processor = EnhancedKeywordProcessor()
    
    for team_key, team_info in teams.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing keywords for: {team_info['team_name']}")
        logger.info(f"{'='*80}")
        
        # Get team sources
        team_source_names = [s["source_name"].lower() for s in team_info["sources"]]
        
        # Get all documents
        all_docs = repo.get_content_by_date_range(start_date, end_date)
        
        # Filter by team sources
        team_docs = []
        for doc in all_docs:
            doc_source_name = (doc.source_name or '').lower()
            if any(team_src in doc_source_name for team_src in team_source_names):
                team_docs.append(doc)
        
        logger.info(f"Found {len(team_docs)} documents for {team_info['team_name']}")
        
        if not team_docs:
            logger.warning(f"No documents to process for {team_info['team_name']}")
            continue
        
        # Group by date
        docs_by_date = {}
        for doc in team_docs:
            date_key = doc.published_date.date() if doc.published_date else datetime.now().date()
            if date_key not in docs_by_date:
                docs_by_date[date_key] = []
            docs_by_date[date_key].append(doc)
        
        # Process all documents for this team
        successful = 0
        failed = 0
        total_keywords = 0
        
        for doc in team_docs:
            try:
                extraction_date = doc.published_date.date() if doc.published_date else datetime.now().date()
                
                result = processor.process_content(
                    content_id=doc.id,
                    title=doc.title or "",
                    content=doc.content or "",
                    source_type=doc.source_type,
                    source_name=doc.source_name,
                    published_date=doc.published_date,
                    extraction_date=extraction_date,
                    team_key=team_key,
                )
                
                if result.get('keywords_extracted', 0) > 0:
                    successful += 1
                    total_keywords += result['keywords_extracted']
                    
            except Exception as e:
                logger.error(f"Error processing document {doc.id}: {str(e)}")
                failed += 1
        
        logger.info(f"✓ Processed {successful}/{len(team_docs)} documents, extracted {total_keywords} keywords")
        
        # Calculate importance for all accumulated keywords
        if processor.keyword_cache:
            logger.info(f"Calculating importance for {len(processor.keyword_cache)} unique keywords...")
            
            # Group by date for importance calculation
            for process_date in sorted(docs_by_date.keys()):
                logger.info(f"Calculating importance for {process_date}...")
                result = processor.calculate_importance_and_sentiment(
                    analysis_date=process_date,
                    team_key=team_key,
                    min_frequency=1
                )
                logger.info(f"✓ Saved {result['keywords_saved']} importance records for {process_date}")
            
            # Clear cache for next team
            processor.keyword_cache = defaultdict(lambda: {'frequency': 0, 'documents': [], 'content_ids': []})
    
    session.close()
    
    logger.info(f"\n{'='*80}")
    logger.info("KEYWORD PROCESSING COMPLETE")
    logger.info(f"{'='*80}\n")


def main():
    """Main execution."""
    logger.info(f"\n{'#'*80}")
    logger.info("# STARTING FULL DATA PIPELINE")
    logger.info(f"{'#'*80}\n")
    
    # Step 1: Fetch all documents
    logger.info("STEP 1: Fetching documents from all sources...")
    asyncio.run(fetch_all_sources())
    
    # Step 2: Process keywords
    logger.info("\nSTEP 2: Processing keywords...")
    process_keywords()
    
    logger.info(f"\n{'#'*80}")
    logger.info("# PIPELINE COMPLETE")
    logger.info(f"{'#'*80}\n")


if __name__ == "__main__":
    main()
