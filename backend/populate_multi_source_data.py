#!/usr/bin/env python3
"""
Populate Data Lake with Multi-Source Content

This script fetches content from ALL configured sources (RSS, Reddit, NewsAPI)
and stores them permanently for processing.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.data_sourcing_service import DataSourcingService
from teams.repository import TeamRepository

print("="*80)
print("POPULATING DATA LAKE WITH MULTI-SOURCE CONTENT")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


async def main():
    """Fetch from all sources and populate data lake."""
    
    service = DataSourcingService()
    team_repo = TeamRepository()
    
    # Show configured sources
    teams = [t for t in team_repo.get_all_teams() if t.is_active]
    
    source_summary = defaultdict(lambda: defaultdict(int))
    
    print("Configured Sources by Team:")
    print("-" * 80)
    
    for team in teams:
        print(f"\n{team.team_name}:")
        enabled_sources = [s for s in team.sources if s.is_enabled]
        
        for source in enabled_sources:
            source_type = source.source_type
            source_summary[team.team_key][source_type] += 1
            print(f"  • [{source_type.upper()}] {source.source_name}")
    
    print(f"\n{'='*80}")
    print("Source Type Summary:")
    for team_key, types in source_summary.items():
        print(f"  {team_key}: {dict(types)}")
    
    # Ask to proceed
    print(f"\n{'='*80}")
    print("This will fetch content from ALL sources and store in data lake.")
    print("Press Enter to continue...")
    input()
    
    # Fetch from ALL sources
    print(f"\n{'='*80}")
    print("FETCHING FROM ALL SOURCES")
    print("="*80)
    
    results = await service.fetch_all_sources()
    
    # Analyze results
    by_type = defaultdict(lambda: {'success': 0, 'failed': 0, 'new': 0, 'total': 0})
    
    for r in results:
        source_type = r.get('type', 'unknown')
        if r['success']:
            by_type[source_type]['success'] += 1
            by_type[source_type]['new'] += r.get('new', 0)
            by_type[source_type]['total'] += r.get('total_fetched', 0)
        else:
            by_type[source_type]['failed'] += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("FETCH RESULTS")
    print("="*80)
    
    total_new = 0
    total_fetched = 0
    
    for source_type in sorted(by_type.keys()):
        stats = by_type[source_type]
        print(f"\n{source_type.upper()}:")
        print(f"  • Sources: {stats['success']} succeeded, {stats['failed']} failed")
        print(f"  • Documents: {stats['total']} fetched, {stats['new']} new")
        total_new += stats['new']
        total_fetched += stats['total']
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {total_fetched} documents fetched, {total_new} NEW documents added to data lake")
    print("="*80)
    
    # Show which sources contributed
    print(f"\nSource Types in Data Lake:")
    for source_type in sorted(by_type.keys()):
        if by_type[source_type]['new'] > 0:
            print(f"  ✓ {source_type.upper()}")
    
    print(f"\nNext Steps:")
    print(f"  1. Process content: python3 scripts/process_all_content.py process")
    print(f"  2. Query keywords: python3 query_multi_source_keywords.py")
    print(f"  3. View JSON: cat output/multi_source_keywords.json")
    print()
    
    service.content_repo.close()
    service.team_repo.close()
    team_repo.close()


if __name__ == "__main__":
    asyncio.run(main())
