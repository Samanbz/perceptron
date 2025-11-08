"""
Test script to demonstrate multi-source integration.

This script:
1. Tests individual sourcers in isolation
2. Loads sources from config.json
3. Fetches data from multiple source types
4. Stores in database
5. Processes with NLP pipeline
6. Generates keywords and importance scores

Usage:
    python test_multi_source_integration.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date
import logging
import json
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from storage.repository import ContentRepository
from keywords import EnhancedKeywordProcessor
from teams.repository import TeamRepository
from sourcers import (
    RSSSourcer,
    RedditSourcer,
    TwitterSourcer,
    YouTubeSourcer,
    NewsAPISourcer,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiSourceIntegrationTest:
    """Test multi-source data ingestion and processing."""
    
    def __init__(self):
        self.content_repo = ContentRepository()
        self.team_repo = TeamRepository()
    
    async def test_individual_sourcer(self, sourcer_name: str, sourcer_instance):
        """Test a single sourcer in isolation."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing {sourcer_name}")
        logger.info(f"{'='*80}")
        
        try:
            contents = await sourcer_instance.fetch()
            logger.info(f"✓ Successfully fetched {len(contents)} items")
            
            # Show sample
            if contents:
                sample = contents[0]
                logger.info(f"\nSample item:")
                logger.info(f"  Title: {sample.title[:80]}...")
                logger.info(f"  Published: {sample.published_date}")
                logger.info(f"  Content length: {len(sample.content)} chars")
            
            return {
                'sourcer': sourcer_name,
                'success': True,
                'count': len(contents),
                'sample': contents[0] if contents else None
            }
            
        except ImportError as e:
            logger.warning(f"⚠ {sourcer_name}: Missing dependency - {e}")
            logger.info(f"   To use this sourcer, install required package")
            return {
                'sourcer': sourcer_name,
                'success': False,
                'error': f"Missing dependency: {str(e)}"
            }
        except Exception as e:
            logger.error(f"✗ {sourcer_name}: {e}")
            return {
                'sourcer': sourcer_name,
                'success': False,
                'error': str(e)
            }
    
    async def test_all_sourcers(self):
        """Test all available sourcers."""
        logger.info("\n" + "="*80)
        logger.info("PHASE 1: Testing Individual Sourcers")
        logger.info("="*80)
        
        tests = []
        
        # Test RSS (always available)
        logger.info("\n1. Testing RSS Sourcer (TechCrunch)")
        rss = RSSSourcer(
            feed_url="https://techcrunch.com/feed/",
            name="TechCrunch Test",
            max_entries=5
        )
        tests.append(await self.test_individual_sourcer("RSS", rss))
        
        # Test Reddit (requires credentials)
        logger.info("\n2. Testing Reddit Sourcer (r/technology)")
        try:
            reddit = RedditSourcer(
                subreddit="technology",
                name="Reddit Test",
                limit=5,
                time_filter="day",
                sort_by="hot"
            )
            tests.append(await self.test_individual_sourcer("Reddit", reddit))
        except ValueError as e:
            logger.warning(f"⚠ Reddit: {e}")
            logger.info("   Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to test Reddit")
            tests.append({
                'sourcer': 'Reddit',
                'success': False,
                'error': 'Missing credentials'
            })
        
        # Test NewsAPI (requires API key)
        logger.info("\n3. Testing NewsAPI Sourcer")
        try:
            newsapi = NewsAPISourcer(
                query="artificial intelligence",
                name="NewsAPI Test",
                max_articles=5
            )
            tests.append(await self.test_individual_sourcer("NewsAPI", newsapi))
        except ValueError as e:
            logger.warning(f"⚠ NewsAPI: {e}")
            logger.info("   Set NEWSAPI_KEY to test NewsAPI")
            tests.append({
                'sourcer': 'NewsAPI',
                'success': False,
                'error': 'Missing API key'
            })
        
        # Test YouTube (requires API key)
        logger.info("\n4. Testing YouTube Sourcer")
        try:
            youtube = YouTubeSourcer(
                search_query="machine learning tutorial",
                name="YouTube Test",
                max_results=5
            )
            tests.append(await self.test_individual_sourcer("YouTube", youtube))
        except ValueError as e:
            logger.warning(f"⚠ YouTube: {e}")
            logger.info("   Set YOUTUBE_API_KEY to test YouTube")
            tests.append({
                'sourcer': 'YouTube',
                'success': False,
                'error': 'Missing API key'
            })
        
        # Test Twitter (no credentials needed, uses Nitter)
        logger.info("\n5. Testing Twitter Sourcer")
        try:
            twitter = TwitterSourcer(
                search_query="AI regulation",
                name="Twitter Test",
                max_tweets=5,
                mode="term"
            )
            tests.append(await self.test_individual_sourcer("Twitter", twitter))
        except ImportError as e:
            logger.warning(f"⚠ Twitter: {e}")
            tests.append({
                'sourcer': 'Twitter',
                'success': False,
                'error': 'Missing ntscraper package'
            })
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("Sourcer Test Summary")
        logger.info(f"{'='*80}")
        successful = [t for t in tests if t['success']]
        logger.info(f"✓ {len(successful)}/{len(tests)} sourcers working")
        for test in tests:
            status = "✓" if test['success'] else "✗"
            logger.info(f"  {status} {test['sourcer']}")
        
        return tests
    
    async def test_config_integration(self):
        """Test loading and fetching from config.json sources."""
        logger.info("\n" + "="*80)
        logger.info("PHASE 2: Testing Config Integration")
        logger.info("="*80)
        
        # Load config
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Count sources by type
        source_counts = {}
        for team in config['teams']:
            for source in team['sources']:
                if source.get('is_enabled', True):
                    source_type = source['source_type']
                    source_counts[source_type] = source_counts.get(source_type, 0) + 1
        
        logger.info(f"\nSources configured in config.json:")
        for source_type, count in sorted(source_counts.items()):
            logger.info(f"  {source_type}: {count} sources")
        
        # Test a sample from each team
        logger.info(f"\n{'='*80}")
        logger.info("Testing one source from each team")
        logger.info(f"{'='*80}")
        
        results = []
        for team in config['teams']:
            team_name = team['team_name']
            enabled_sources = [s for s in team['sources'] if s.get('is_enabled', True)]
            
            if not enabled_sources:
                logger.info(f"\n{team_name}: No enabled sources")
                continue
            
            # Test first enabled source
            source = enabled_sources[0]
            logger.info(f"\n{team_name}: Testing {source['source_name']} ({source['source_type']})")
            
            try:
                from services.data_sourcing_service import DataSourcingService
                service = DataSourcingService()
                
                result = await service.fetch_from_source({
                    'name': source['source_name'],
                    'url': source.get('source_url', ''),
                    'type': source['source_type'],
                    'config': source.get('config', {})
                })
                
                results.append(result)
                
                if result['success']:
                    logger.info(
                        f"  ✓ Fetched: {result.get('total_fetched', 0)} items, "
                        f"Saved: {result['new']} new, {result['duplicates']} duplicates"
                    )
                else:
                    logger.warning(f"  ✗ Error: {result.get('error', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"  ✗ Failed: {e}")
                results.append({
                    'source': source['source_name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def test_nlp_processing(self):
        """Test NLP processing on collected data."""
        logger.info("\n" + "="*80)
        logger.info("PHASE 3: Testing NLP Processing")
        logger.info("="*80)
        
        # Get unprocessed content
        unprocessed = self.content_repo.get_unprocessed_content()
        logger.info(f"\nUnprocessed content items: {len(unprocessed)}")
        
        if not unprocessed:
            logger.warning("No unprocessed content found. Run data sourcing first.")
            return None
        
        # Process for each team
        teams = [t for t in self.team_repo.get_all_teams() if t.is_active]
        results = []
        
        for team in teams:
            logger.info(f"\n{team.team_name}:")
            
            # Get team-specific content
            team_sources = [s.source_name for s in team.sources if s.is_enabled]
            team_content = [
                c for c in unprocessed 
                if c.source_name in team_sources
            ]
            
            if not team_content:
                logger.info(f"  No content from team sources")
                continue
            
            logger.info(f"  Processing {len(team_content)} items...")
            
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
            
            # Mark as processed
            for content in team_content:
                self.content_repo.mark_as_processed(content.id, status='completed')
            
            processor.close()
            
            logger.info(
                f"  ✓ Keywords: {result['keywords_stored']}, "
                f"Importance: {result.get('importance_calculation', {}).get('keywords_saved', 0)}"
            )
            
            # Show top keywords
            if result.get('top_keywords'):
                logger.info(f"  Top keywords:")
                for kw, score in result['top_keywords'][:5]:
                    logger.info(f"    - {kw}: {score:.4f}")
            
            results.append({
                'team': team.team_name,
                'items_processed': len(team_content),
                'keywords_stored': result['keywords_stored'],
                'top_keywords': result.get('top_keywords', [])[:10]
            })
        
        return results
    
    async def run_full_test(self):
        """Run complete integration test."""
        logger.info("\n" + "="*80)
        logger.info("MULTI-SOURCE INTEGRATION TEST")
        logger.info("="*80)
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Phase 1: Test individual sourcers
        sourcer_results = await self.test_all_sourcers()
        
        # Phase 2: Test config integration
        config_results = await self.test_config_integration()
        
        # Phase 3: Test NLP processing
        nlp_results = self.test_nlp_processing()
        
        # Final summary
        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETE - SUMMARY")
        logger.info("="*80)
        
        logger.info(f"\n1. Sourcer Tests:")
        working_sourcers = [r for r in sourcer_results if r['success']]
        logger.info(f"   ✓ {len(working_sourcers)}/{len(sourcer_results)} sourcers operational")
        
        if config_results:
            logger.info(f"\n2. Config Integration:")
            successful_fetches = [r for r in config_results if r.get('success')]
            total_new = sum(r.get('new', 0) for r in successful_fetches)
            logger.info(f"   ✓ {len(successful_fetches)} sources fetched successfully")
            logger.info(f"   ✓ {total_new} new documents added to data lake")
        
        if nlp_results:
            logger.info(f"\n3. NLP Processing:")
            total_keywords = sum(r['keywords_stored'] for r in nlp_results)
            logger.info(f"   ✓ {len(nlp_results)} teams processed")
            logger.info(f"   ✓ {total_keywords} keywords extracted")
            
            # Show top keywords across all teams
            logger.info(f"\n   Top keywords by team:")
            for result in nlp_results:
                logger.info(f"\n   {result['team']}:")
                for kw, score in result['top_keywords'][:5]:
                    logger.info(f"     - {kw}: {score:.4f}")
        
        logger.info(f"\n{'='*80}")
        logger.info("✓ Integration test complete!")
        logger.info("="*80)
    
    def close(self):
        """Clean up resources."""
        self.content_repo.close()
        self.team_repo.close()


async def main():
    """Main entry point."""
    test = MultiSourceIntegrationTest()
    
    try:
        await test.run_full_test()
    finally:
        test.close()


if __name__ == "__main__":
    asyncio.run(main())
