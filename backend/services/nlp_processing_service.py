"""
Perpetual NLP Processing Service

Continuously processes new content through the NLP pipeline.
- Runs every 5 minutes
- Processes all unprocessed content for all teams
- Calculates keywords, importance, sentiment
- Generates time-series data
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import logging
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.repository import ContentRepository
from keywords import EnhancedKeywordProcessor
from teams.repository import TeamRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NLPProcessingService:
    """Perpetual NLP processing service."""
    
    def __init__(self):
        self.content_repo = ContentRepository()
        self.team_repo = TeamRepository()
        self.check_interval_seconds = 300  # 5 minutes
        
    def process_for_team(self, team, unprocessed_content):
        """Process content for a single team."""
        team_sources = [s.source_name for s in team.sources if s.is_enabled]
        team_content = [
            c for c in unprocessed_content 
            if c.source_name in team_sources
        ]
        
        if not team_content:
            return None
        
        logger.info(f"\n{team.team_name}: Processing {len(team_content)} items...")
        
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
                'extraction_date': content.published_date.date() if content.published_date else date.today(),
            }
            for content in team_content
        ]
        
        # Process batch
        result = processor.process_batch(
            content_items=content_items,
            team_key=team.team_key,
            calculate_importance=True,
        )
        
        # Generate time-series for last 7 days
        processor.generate_timeseries(team_key=team.team_key, days=7)
        
        # Mark as processed
        for content in team_content:
            self.content_repo.mark_as_processed(content.id, status='completed')
        
        processor.close()
        
        logger.info(
            f"  ✓ Keywords: {result['keywords_stored']}, "
            f"Importance: {result.get('importance_calculation', {}).get('keywords_saved', 0)}"
        )
        
        return result
    
    def run_once(self):
        """Run one processing cycle."""
        # Get all unprocessed content
        unprocessed = self.content_repo.get_unprocessed_content()
        
        if not unprocessed:
            logger.info("No unprocessed content")
            return
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing {len(unprocessed)} unprocessed items")
        logger.info(f"{'='*80}")
        
        # Get all active teams
        teams = [t for t in self.team_repo.get_all_teams() if t.is_active]
        
        # Process for each team
        total_keywords = 0
        for team in teams:
            result = self.process_for_team(team, unprocessed)
            if result:
                total_keywords += result.get('keywords_stored', 0)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing complete: {total_keywords} total keywords")
        logger.info(f"{'='*80}\n")
    
    def run_forever(self):
        """Run perpetually, checking every 5 minutes."""
        logger.info("="*80)
        logger.info("NLP PROCESSING SERVICE STARTED")
        logger.info("="*80)
        logger.info(f"Check interval: {self.check_interval_seconds}s ({self.check_interval_seconds/60}min)")
        logger.info("="*80 + "\n")
        
        while True:
            try:
                self.run_once()
                
                logger.info(f"Waiting {self.check_interval_seconds}s...")
                logger.info(f"Next check at: {(time.time() + self.check_interval_seconds)}\n")
                
                time.sleep(self.check_interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("\nShutting down...")
                break
            except Exception as e:
                logger.error(f"Error in processing cycle: {e}")
                logger.info("Waiting 60s before retry...")
                time.sleep(60)
        
        self.content_repo.close()
        self.team_repo.close()


def main():
    """Main entry point."""
    service = NLPProcessingService()
    
    # Initial run
    service.run_once()
    
    # Ask if user wants to run perpetually
    print("\nRun perpetually? (y/n): ", end='', flush=True)
    choice = input().strip().lower()
    
    if choice == 'y':
        service.run_forever()
    else:
        service.content_repo.close()
        service.team_repo.close()
        print("Exiting.")


if __name__ == "__main__":
    main()
