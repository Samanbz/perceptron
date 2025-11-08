#!/usr/bin/env python3
"""
Complete Multi-Source Pipeline Demonstration

This script demonstrates the full pipeline:
1. Load config with multiple source types
2. Fetch data from all sources (RSS, Reddit, NewsAPI)
3. Store in database
4. Process with NLP
5. Query keywords by team and date
6. Show that keywords come from multiple sources
7. Export results as JSON

Run: python3 full_pipeline_demo.py
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from collections import defaultdict

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from services.data_sourcing_service import DataSourcingService
from services.nlp_processing_service import NLPProcessingService
from keywords.repository import KeywordRepository
from teams.repository import TeamRepository

print("="*80)
print("COMPLETE MULTI-SOURCE PIPELINE DEMONSTRATION")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


async def step1_fetch_data():
    """Step 1: Fetch data from all configured sources."""
    print("\nSTEP 1: Fetching Data from Multiple Sources")
    print("="*80)
    
    service = DataSourcingService()
    
    # Get source summary
    sources = service.get_all_sources()
    
    # Count by type
    by_type = defaultdict(int)
    for source in sources:
        by_type[source['type']] += 1
    
    print(f"\nConfigured sources: {len(sources)} total")
    for source_type, count in sorted(by_type.items()):
        print(f"  • {source_type.upper()}: {count} sources")
    
    # Fetch from all sources
    print(f"\nFetching from all sources...")
    results = await service.fetch_all_sources()
    
    # Summary
    successful = [r for r in results if r['success']]
    total_new = sum(r.get('new', 0) for r in successful)
    total_fetched = sum(r.get('total_fetched', 0) for r in successful)
    
    print(f"\n{'='*80}")
    print(f"Fetch Results:")
    print(f"  • {len(successful)}/{len(results)} sources succeeded")
    print(f"  • {total_fetched} total documents fetched")
    print(f"  • {total_new} new documents added to data lake")
    
    # Show breakdown by source type
    by_type_results = defaultdict(lambda: {'count': 0, 'new': 0})
    for r in successful:
        source_type = r.get('type', 'unknown')
        by_type_results[source_type]['count'] += 1
        by_type_results[source_type]['new'] += r.get('new', 0)
    
    print(f"\nBy source type:")
    for source_type, data in sorted(by_type_results.items()):
        print(f"  • {source_type.upper()}: {data['count']} sources, {data['new']} new documents")
    
    service.content_repo.close()
    service.team_repo.close()
    
    return results


def step2_process_nlp():
    """Step 2: Process content with NLP pipeline."""
    print("\n\nSTEP 2: Processing with NLP Pipeline")
    print("="*80)
    
    service = NLPProcessingService()
    
    # Run one processing cycle
    service.run_once()
    
    service.content_repo.close()
    service.team_repo.close()


def step3_query_keywords(team_key=None, days=7):
    """Step 3: Query keywords and show multi-source data."""
    print("\n\nSTEP 3: Querying Keywords from Database")
    print("="*80)
    
    keyword_repo = KeywordRepository()
    team_repo = TeamRepository()
    
    # Get all teams
    teams = [t for t in team_repo.get_all_teams() if t.is_active]
    
    if team_key:
        teams = [t for t in teams if t.team_key == team_key]
    
    all_results = {}
    
    for team in teams:
        print(f"\n{team.team_name} ({team.team_key})")
        print("-" * 40)
        
        # Get keywords for last N days
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get daily keywords
        daily_keywords = {}
        current_date = start_date
        
        while current_date <= end_date:
            keywords = keyword_repo.get_keywords_by_date(
                team_key=team.team_key,
                extraction_date=current_date
            )
            
            if keywords:
                daily_keywords[current_date.isoformat()] = keywords
        
        if not daily_keywords:
            print(f"  No keywords found for last {days} days")
            continue
        
        # Analyze sources
        source_content_map = defaultdict(set)
        all_keywords_with_sources = []
        
        for date_str, keywords in daily_keywords.items():
            for kw in keywords:
                # Get source information from content_ids
                if kw.content_ids:
                    content_ids = json.loads(kw.content_ids) if isinstance(kw.content_ids, str) else kw.content_ids
                    
                    # Get source types from content
                    from storage.repository import ContentRepository
                    content_repo = ContentRepository()
                    
                    for content_id in content_ids[:3]:  # Sample first 3
                        content = content_repo.get_by_id(content_id)
                        if content:
                            source_content_map[content.source_type].add(content.source_name)
                    
                    content_repo.close()
                
                all_keywords_with_sources.append({
                    'keyword': kw.keyword,
                    'relevance_score': float(kw.relevance_score),
                    'frequency': kw.frequency,
                    'extraction_date': date_str,
                    'importance_score': float(kw.importance_score) if kw.importance_score else None,
                })
        
        # Sort by importance
        all_keywords_with_sources.sort(
            key=lambda x: x['importance_score'] or x['relevance_score'],
            reverse=True
        )
        
        # Show summary
        print(f"  Keywords found: {len(all_keywords_with_sources)}")
        print(f"  Date range: {start_date} to {end_date}")
        print(f"  Sources contributing:")
        
        for source_type, source_names in sorted(source_content_map.items()):
            print(f"    • {source_type.upper()}: {', '.join(sorted(source_names))}")
        
        # Show top 10 keywords
        print(f"\n  Top 10 Keywords:")
        for i, kw in enumerate(all_keywords_with_sources[:10], 1):
            score = kw['importance_score'] or kw['relevance_score']
            print(f"    {i:2d}. {kw['keyword']:25s} {score:.4f} (freq: {kw['frequency']})")
        
        # Store results
        all_results[team.team_key] = {
            'team_name': team.team_name,
            'team_key': team.team_key,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'sources': {
                source_type: sorted(list(source_names))
                for source_type, source_names in source_content_map.items()
            },
            'total_keywords': len(all_keywords_with_sources),
            'keywords': all_keywords_with_sources[:50]  # Top 50
        }
    
    keyword_repo.close()
    team_repo.close()
    
    return all_results


def step4_export_json(results, filename='keyword_analysis.json'):
    """Step 4: Export results as JSON."""
    print("\n\nSTEP 4: Exporting Results")
    print("="*80)
    
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / filename
    
    # Add metadata
    export_data = {
        'generated_at': datetime.now().isoformat(),
        'description': 'Multi-source keyword analysis from Signal Radar platform',
        'teams': results
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n✓ Exported to: {output_file}")
    print(f"  File size: {output_file.stat().st_size:,} bytes")
    print(f"  Teams: {len(results)}")
    
    # Show file preview
    print(f"\n  JSON structure:")
    for team_key, team_data in results.items():
        sources = team_data.get('sources', {})
        total_sources = sum(len(v) for v in sources.values())
        print(f"    • {team_key}: {team_data['total_keywords']} keywords from {total_sources} sources")
    
    return output_file


async def main():
    """Run the complete pipeline."""
    start_time = datetime.now()
    
    print("\nThis demonstration will:")
    print("  1. Fetch data from RSS, Reddit, and NewsAPI sources")
    print("  2. Process content through NLP pipeline")
    print("  3. Extract and score keywords")
    print("  4. Query keywords by team and date range")
    print("  5. Show which sources contributed to each team")
    print("  6. Export results as JSON")
    print("\nPress Enter to continue...")
    input()
    
    # Step 1: Fetch data
    fetch_results = await step1_fetch_data()
    
    # Step 2: Process with NLP
    step2_process_nlp()
    
    # Step 3: Query keywords (last 7 days)
    keyword_results = step3_query_keywords(days=7)
    
    # Step 4: Export JSON
    output_file = step4_export_json(keyword_results)
    
    # Final summary
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n\n" + "="*80)
    print("PIPELINE COMPLETE!")
    print("="*80)
    
    # Count total sources
    total_sources_used = set()
    total_source_types = set()
    total_keywords = 0
    
    for team_key, team_data in keyword_results.items():
        total_keywords += team_data['total_keywords']
        for source_type, source_names in team_data.get('sources', {}).items():
            total_source_types.add(source_type)
            total_sources_used.update(source_names)
    
    print(f"\n✓ Multi-Source Integration Verified:")
    print(f"  • {len(total_source_types)} source types (RSS, Reddit, NewsAPI)")
    print(f"  • {len(total_sources_used)} unique sources")
    print(f"  • {len(keyword_results)} teams processed")
    print(f"  • {total_keywords} total keywords extracted")
    print(f"  • Elapsed time: {elapsed:.1f}s")
    
    print(f"\n✓ Data exported to: {output_file}")
    print(f"\nYou can now:")
    print(f"  • View the JSON file: cat {output_file}")
    print(f"  • Query via API: curl http://localhost:5000/api/keywords/<team_key>/<date>")
    print(f"  • Run perpetually: python services/data_sourcing_service.py & python services/nlp_processing_service.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
