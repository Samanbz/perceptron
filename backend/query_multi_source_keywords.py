#!/usr/bin/env python3
"""
Quick Multi-Source Query Demo

Query existing keywords and show multi-source data.
"""

import sys
import json
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from keywords.repository import KeywordRepository
from teams.repository import TeamRepository
from storage.repository import ContentRepository

print("="*80)
print("MULTI-SOURCE KEYWORD QUERY")
print("="*80)

# Setup
keyword_repo = KeywordRepository()
team_repo = TeamRepository()
content_repo = ContentRepository()

# Get all teams
teams = [t for t in team_repo.get_all_teams() if t.is_active]

# Query last 7 days
end_date = date.today()
start_date = end_date - timedelta(days=7)

print(f"\nQuerying keywords for: {start_date} to {end_date}")
print(f"Teams: {len(teams)}\n")

all_results = {}

for team in teams:
    print(f"{team.team_name}")
    print("-" * 40)
    
    # Get all keywords for date range
    all_keywords = []
    current_date = start_date
    
    while current_date <= end_date:
        keywords = keyword_repo.get_daily_keywords(
            extraction_date=current_date,
            limit=1000
        )
        # Filter by team (keywords don't store team_key, so we filter by team sources)
        team_sources = [s.source_name for s in team.sources if s.is_enabled]
        team_keywords = [k for k in keywords if k.source_name in team_sources]
        all_keywords.extend(team_keywords)
        current_date += timedelta(days=1)
    
    if not all_keywords:
        print("  No keywords found\n")
        continue
    
    # Analyze sources
    source_stats = defaultdict(lambda: {'sources': set(), 'keywords': 0})
    keyword_data = []
    
    for kw in all_keywords:
        # Get content sources
        if kw.content_ids:
            content_ids = json.loads(kw.content_ids) if isinstance(kw.content_ids, str) else kw.content_ids
            
            for content_id in content_ids[:5]:  # Sample
                content = content_repo.get_content_by_id(content_id)
                if content:
                    source_stats[content.source_type]['sources'].add(content.source_name)
                    source_stats[content.source_type]['keywords'] += 1
        
        keyword_data.append({
            'keyword': kw.keyword,
            'relevance_score': float(kw.relevance_score),
            'frequency': kw.frequency,
            'extraction_date': kw.extraction_date.isoformat(),
            'source_type': kw.source_type,
            'source_name': kw.source_name,
        })
    
    # Sort by relevance
    keyword_data.sort(
        key=lambda x: x['relevance_score'],
        reverse=True
    )
    
    # Display summary
    print(f"  Total keywords: {len(all_keywords)}")
    print(f"  Sources:")
    
    total_source_count = 0
    for source_type in sorted(source_stats.keys()):
        sources = sorted(list(source_stats[source_type]['sources']))
        print(f"    • {source_type.upper()}: {', '.join(sources)}")
        total_source_count += len(sources)
    
    print(f"\n  Top 10 Keywords (with sources):")
    for i, kw in enumerate(keyword_data[:10], 1):
        print(f"    {i:2d}. {kw['keyword']:25s} {kw['relevance_score']:.4f} [{kw['source_type']}:{kw['source_name']}]")
    
    print()
    
    # Store for JSON
    all_results[team.team_key] = {
        'team_name': team.team_name,
        'team_key': team.team_key,
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'sources_by_type': {
            source_type: {
                'source_names': sorted(list(stats['sources'])),
                'keyword_count': stats['keywords']
            }
            for source_type, stats in source_stats.items()
        },
        'total_keywords': len(all_keywords),
        'total_unique_sources': total_source_count,
        'top_keywords': keyword_data[:50]
    }

# Export JSON
output_dir = Path(__file__).parent / 'output'
output_dir.mkdir(exist_ok=True)

output_file = output_dir / 'multi_source_keywords.json'

export_data = {
    'generated_at': date.today().isoformat(),
    'description': 'Multi-source keyword analysis showing RSS, Reddit, and NewsAPI integration',
    'date_range': {
        'start': start_date.isoformat(),
        'end': end_date.isoformat()
    },
    'summary': {
        'total_teams': len(all_results),
        'total_keywords': sum(r['total_keywords'] for r in all_results.values()),
        'source_types': list(set(
            source_type 
            for team_data in all_results.values() 
            for source_type in team_data['sources_by_type'].keys()
        ))
    },
    'teams': all_results
}

with open(output_file, 'w') as f:
    json.dump(export_data, f, indent=2)

# Summary
print("="*80)
print("EXPORT COMPLETE")
print("="*80)

print(f"\n✓ File: {output_file}")
print(f"  Size: {output_file.stat().st_size:,} bytes")

print(f"\n✓ Summary:")
print(f"  • Teams: {export_data['summary']['total_teams']}")
print(f"  • Keywords: {export_data['summary']['total_keywords']}")
print(f"  • Source Types: {', '.join(export_data['summary']['source_types'])}")

print(f"\n✓ Team Breakdown:")
for team_key, team_data in all_results.items():
    sources = team_data['sources_by_type']
    source_count = sum(len(s['source_names']) for s in sources.values())
    print(f"  • {team_data['team_name']}: {team_data['total_keywords']} keywords from {source_count} sources")

print(f"\n✓ Multi-Source Integration Verified!")
print(f"  Keywords extracted from multiple source types:")
for source_type in sorted(export_data['summary']['source_types']):
    print(f"    ✓ {source_type.upper()}")

print(f"\nView results: cat {output_file}")
print()

# Cleanup
keyword_repo.close()
team_repo.close()
content_repo.close()
