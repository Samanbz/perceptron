"""
Reprocess documents for specific dates and a single team.

Usage (run from backend/):
  ./venv/bin/python3 scripts/reprocess_specific_dates.py regulator 2025-11-04 2025-11-05 2025-11-06 2025-11-07

This will process each specified date and assign keywords/importance to the published date.
"""
import sys
import logging
from datetime import datetime, date
from collections import defaultdict

sys.path.insert(0, '/Users/samanb/dev/perceptron/backend')

from keywords.enhanced_processor import EnhancedKeywordProcessor
from storage.repository import ContentRepository
from teams.repository import TeamRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def reprocess_dates_for_team(team_key: str, dates):
    team_repo = TeamRepository()
    content_repo = ContentRepository()

    team = team_repo.get_team_by_key(team_key)
    if not team:
        logger.error(f"Team {team_key} not found")
        return

    processor = EnhancedKeywordProcessor(team_key=team_key)

    total_saved = 0

    for d in dates:
        try:
            pub_date = date.fromisoformat(d)
        except Exception:
            logger.error(f"Invalid date format: {d}")
            continue

        logger.info(f"Processing date {pub_date} for team {team_key}")

        # Fetch documents published on this date
        start_dt = datetime.combine(pub_date, datetime.min.time())
        end_dt = datetime.combine(pub_date, datetime.max.time())
        docs = content_repo.get_content_by_date_range(start_dt, end_dt)
        logger.info(f"Found {len(docs)} documents for {pub_date}")

        if not docs:
            continue

        content_items = []
        for doc in docs:
            content_items.append({
                'id': doc.id,
                'title': doc.title or '',
                'content': doc.content or '',
                'source_type': doc.source_type,
                'source_name': doc.source_name,
                'published_date': doc.published_date,
                'extraction_date': pub_date,
            })

        result = processor.process_batch(content_items, team_key=team_key, calculate_importance=False)
        logger.info(f"  Extracted: {result['successful']} successful, {result['keywords_extracted']} keywords")

        importance_result = processor.calculate_importance_and_sentiment(analysis_date=pub_date, team_key=team_key)
        logger.info(f"  Importance: processed {importance_result.get('keywords_processed',0)}, saved {importance_result.get('keywords_saved',0)}")

        total_saved += importance_result.get('keywords_saved', 0)

    logger.info(f"Reprocessing complete for team {team_key}. Total keywords saved: {total_saved}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: reprocess_specific_dates.py <team_key> <date1> [date2 date3 ...]")
        sys.exit(1)

    team_key = sys.argv[1]
    dates = sys.argv[2:]
    reprocess_dates_for_team(team_key, dates)
