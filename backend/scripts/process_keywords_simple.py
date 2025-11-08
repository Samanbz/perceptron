#!/usr/bin/env python3
"""
Process keywords from existing documents in database.
Simple version that just processes what we have.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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


def main():
    """Process keywords for all teams."""
    logger.info("=" * 80)
    logger.info("PROCESSING KEYWORDS FROM EXISTING DOCUMENTS")
    logger.info("=" * 80)
    
    # Load config for team information
    config = load_config()
    teams = {team["team_key"]: team for team in config["teams"] if team.get("is_active", True)}
    
    # Get documents
    session = get_session()
    repo = ContentRepository(session)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    logger.info(f"Getting documents from {start_date.date()} to {end_date.date()}")
    all_docs = repo.get_content_by_date_range(start_date, end_date)
    logger.info(f"Found {len(all_docs)} total documents")
    
    # Process each team
    processor = EnhancedKeywordProcessor()
    
    for team_key, team_info in teams.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"TEAM: {team_info['team_name']}")
        logger.info(f"{'='*80}")
        
        # Get team sources
        team_source_names = [s["source_name"].lower() for s in team_info["sources"]]
        logger.info(f"Team sources: {', '.join(team_source_names[:3])}... ({len(team_source_names)} total)")
        
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
        
        # Group documents by published date
        docs_by_date = {}
        for doc in team_docs:
            date_key = doc.published_date.date() if doc.published_date else datetime.now().date()
            if date_key not in docs_by_date:
                docs_by_date[date_key] = []
            docs_by_date[date_key].append(doc)
        
        logger.info(f"Documents span {len(docs_by_date)} dates: {sorted(docs_by_date.keys())}")
        
        # Process each date separately to maintain date association
        total_processed = 0
        total_keywords_saved = 0
        
        for process_date in sorted(docs_by_date.keys()):
            docs_for_date = docs_by_date[process_date]
            logger.info(f"\n📅 Processing {process_date}: {len(docs_for_date)} documents")
            
            # Clear cache for this date
            processor.keyword_cache = defaultdict(lambda: {
                'frequency': 0,
                'documents': [],
                'snippets': [],
                'content_ids': [],
            })
            
            # Process documents for this specific date
            successful = 0
            for i, doc in enumerate(docs_for_date):
                try:
                    result = processor.process_content(
                        content_id=doc.id,
                        title=doc.title or "",
                        content=doc.content or "",
                        source_type=doc.source_type,
                        source_name=doc.source_name,
                        published_date=doc.published_date,
                        extraction_date=process_date,  # Use the date we're processing
                        team_key=team_key,
                    )
                    
                    if result.get('keywords_extracted', 0) > 0:
                        successful += 1
                        
                except Exception as e:
                    logger.error(f"Error processing document {doc.id}: {str(e)}")
            
            logger.info(f"  ✓ Extracted from {successful}/{len(docs_for_date)} documents")
            total_processed += successful
            
            # Calculate importance for keywords from this date
            if processor.keyword_cache:
                unique_keywords = len(processor.keyword_cache)
                logger.info(f"  📊 Calculating importance for {unique_keywords} unique keywords...")
                
                result = processor.calculate_importance_and_sentiment(
                    analysis_date=process_date,
                    team_key=team_key,
                    min_frequency=1
                )
                
                keywords_saved = result['keywords_saved']
                total_keywords_saved += keywords_saved
                logger.info(f"  ✅ Saved {keywords_saved} keywords for {process_date}")
            else:
                logger.warning(f"  ⚠️  No keywords in cache for {process_date}")
        
        logger.info(f"\n{'─'*80}")
        logger.info(f"✅ {team_info['team_name']} Complete:")
        logger.info(f"   Documents: {total_processed}/{len(team_docs)}")
        logger.info(f"   Keywords:  {total_keywords_saved} across {len(docs_by_date)} dates")
        logger.info(f"{'─'*80}")
    
    session.close()
    
    logger.info(f"\n{'='*80}")
    logger.info("PROCESSING COMPLETE!")
    logger.info(f"{'='*80}")


if __name__ == "__main__":
    main()
