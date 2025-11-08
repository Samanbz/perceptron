#!/usr/bin/env python3
"""
Fetch keywords for all teams for the last 7 days and save as JSON files.
Generates both daily keyword files and time-series data.
"""

import requests
from datetime import date, timedelta
from pathlib import Path
import json
from typing import Dict, List, Any


# Configuration
API_BASE_URL = "http://localhost:8000"
OUTPUT_DIR = Path("generated_keywords")
DAYS_TO_FETCH = 7
KEYWORDS_PER_DAY = 100


def ensure_output_dir():
    """Create output directory structure."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "daily").mkdir(exist_ok=True)
    (OUTPUT_DIR / "timeseries").mkdir(exist_ok=True)
    print(f"✓ Output directory: {OUTPUT_DIR.absolute()}")


def get_teams() -> List[Dict[str, Any]]:
    """Fetch all teams from API."""
    response = requests.get(f"{API_BASE_URL}/api/teams")
    response.raise_for_status()
    return response.json()["teams"]


def fetch_keywords_for_day(team_key: str, date_str: str, limit: int = 100) -> Dict[str, Any]:
    """Fetch keywords for a specific team and date."""
    params = {
        "date": date_str,
        "team": team_key,
        "limit": limit,
        "min_score": 0
    }
    response = requests.get(f"{API_BASE_URL}/api/keywords", params=params)
    response.raise_for_status()
    return response.json()


def generate_daily_files():
    """Generate daily keyword JSON files for each team."""
    print("\n" + "="*80)
    print("GENERATING DAILY KEYWORD FILES")
    print("="*80 + "\n")
    
    teams = get_teams()
    end_date = date.today()
    start_date = end_date - timedelta(days=DAYS_TO_FETCH - 1)
    
    total_files = 0
    total_keywords = 0
    
    for team in teams:
        team_key = team["team_key"]
        team_name = team["team_name"]
        
        print(f"📁 {team_name} ({team_key})")
        print("-" * 80)
        
        team_total = 0
        
        for day_offset in range(DAYS_TO_FETCH):
            current_date = start_date + timedelta(days=day_offset)
            date_str = current_date.strftime('%Y-%m-%d')
            
            try:
                data = fetch_keywords_for_day(team_key, date_str, KEYWORDS_PER_DAY)
                
                # Save to file
                filename = f"{team_key}_{date_str}.json"
                filepath = OUTPUT_DIR / "daily" / filename
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                
                keyword_count = data["count"]
                team_total += keyword_count
                total_keywords += keyword_count
                total_files += 1
                
                print(f"  ✓ {date_str}: {keyword_count:3d} keywords → {filename}")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"  ⊘ {date_str}: No data available")
                else:
                    print(f"  ✗ {date_str}: Error - {e}")
            except Exception as e:
                print(f"  ✗ {date_str}: Error - {e}")
        
        print(f"  Total: {team_total} keywords\n")
    
    print("="*80)
    print(f"✓ Generated {total_files} daily files with {total_keywords} total keywords")
    print("="*80)


def build_timeseries_from_daily_files(team_key: str) -> Dict[str, Any]:
    """Build time-series data from daily keyword files."""
    daily_dir = OUTPUT_DIR / "daily"
    team_files = sorted(daily_dir.glob(f"{team_key}_*.json"))
    
    if not team_files:
        return {}
    
    # Track each keyword across days
    keyword_timeseries = {}
    
    for filepath in team_files:
        with open(filepath) as f:
            data = json.load(f)
        
        date_str = data["date"]
        
        for kw in data["keywords"]:
            keyword_text = kw["keyword"]
            
            if keyword_text not in keyword_timeseries:
                keyword_timeseries[keyword_text] = {
                    "keyword": keyword_text,
                    "team_key": team_key,
                    "data_points": []
                }
            
            # Add data point for this date
            keyword_timeseries[keyword_text]["data_points"].append({
                "date": date_str,
                "importance_score": kw["importance_score"],
                "sentiment_score": kw["sentiment"]["score"],
                "frequency": kw["metrics"]["frequency"],
                "document_count": kw["metrics"]["document_count"]
            })
    
    # Calculate statistics for each keyword
    for kw_data in keyword_timeseries.values():
        points = kw_data["data_points"]
        kw_data["appearances"] = len(points)
        kw_data["avg_importance"] = sum(p["importance_score"] for p in points) / len(points)
        kw_data["max_importance"] = max(p["importance_score"] for p in points)
        kw_data["total_frequency"] = sum(p["frequency"] for p in points)
        kw_data["total_documents"] = sum(p["document_count"] for p in points)
        
        # Sort data points by date
        kw_data["data_points"].sort(key=lambda x: x["date"])
    
    return keyword_timeseries


def generate_timeseries_files():
    """Generate time-series JSON files for top keywords per team."""
    print("\n" + "="*80)
    print("GENERATING TIME-SERIES FILES")
    print("="*80 + "\n")
    
    teams = get_teams()
    total_files = 0
    
    for team in teams:
        team_key = team["team_key"]
        team_name = team["team_name"]
        
        print(f"📈 {team_name} ({team_key})")
        print("-" * 80)
        
        # Build time-series from daily files
        timeseries_data = build_timeseries_from_daily_files(team_key)
        
        if not timeseries_data:
            print(f"  ⊘ No data available\n")
            continue
        
        # Sort keywords by consistency (appearances) and importance
        sorted_keywords = sorted(
            timeseries_data.values(),
            key=lambda x: (x["appearances"], x["max_importance"]),
            reverse=True
        )
        
        # Save aggregate file with all keywords
        aggregate_file = OUTPUT_DIR / "timeseries" / f"{team_key}_timeseries_all.json"
        with open(aggregate_file, 'w') as f:
            json.dump({
                "team_key": team_key,
                "team_name": team_name,
                "total_keywords": len(sorted_keywords),
                "keywords": sorted_keywords[:50]  # Top 50
            }, f, indent=2)
        
        print(f"  ✓ All keywords: {len(sorted_keywords)} total → {aggregate_file.name}")
        total_files += 1
        
        # Save individual files for top 10 keywords
        for i, kw_data in enumerate(sorted_keywords[:10], 1):
            keyword_safe = kw_data["keyword"].replace(" ", "_").replace("/", "-")
            filename = f"{team_key}_{keyword_safe}_timeseries.json"
            filepath = OUTPUT_DIR / "timeseries" / filename
            
            with open(filepath, 'w') as f:
                json.dump(kw_data, f, indent=2)
            
            print(f"  {i:2d}. '{kw_data['keyword']}': {kw_data['appearances']} days, "
                  f"avg score {kw_data['avg_importance']:.2f} → {filename}")
            total_files += 1
        
        print()
    
    print("="*80)
    print(f"✓ Generated {total_files} time-series files")
    print("="*80)


def generate_summary():
    """Generate summary statistics file."""
    print("\n" + "="*80)
    print("GENERATING SUMMARY")
    print("="*80 + "\n")
    
    daily_dir = OUTPUT_DIR / "daily"
    timeseries_dir = OUTPUT_DIR / "timeseries"
    
    daily_files = list(daily_dir.glob("*.json"))
    timeseries_files = list(timeseries_dir.glob("*.json"))
    
    # Count keywords by team
    team_stats = {}
    for filepath in daily_files:
        with open(filepath) as f:
            data = json.load(f)
        
        team_key = data["team"]
        if team_key not in team_stats:
            team_stats[team_key] = {"files": 0, "total_keywords": 0, "dates": set()}
        
        team_stats[team_key]["files"] += 1
        team_stats[team_key]["total_keywords"] += data["count"]
        team_stats[team_key]["dates"].add(data["date"])
    
    # Convert sets to lists for JSON serialization
    for stats in team_stats.values():
        stats["dates"] = sorted(list(stats["dates"]))
        stats["days"] = len(stats["dates"])
    
    summary = {
        "generated_at": date.today().isoformat(),
        "days_covered": DAYS_TO_FETCH,
        "total_daily_files": len(daily_files),
        "total_timeseries_files": len(timeseries_files),
        "team_statistics": team_stats,
        "directories": {
            "daily": str(daily_dir),
            "timeseries": str(timeseries_dir)
        }
    }
    
    summary_file = OUTPUT_DIR / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary Statistics:")
    print(f"  Daily files:      {len(daily_files)}")
    print(f"  Time-series files: {len(timeseries_files)}")
    print(f"  Teams processed:   {len(team_stats)}")
    print(f"  Days covered:      {DAYS_TO_FETCH}")
    print(f"\n✓ Saved summary to {summary_file}")


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("KEYWORD DATA EXPORT")
    print("="*80)
    print(f"Fetching keywords for last {DAYS_TO_FETCH} days")
    print(f"API: {API_BASE_URL}")
    print("="*80)
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        response.raise_for_status()
        print("✓ API is healthy\n")
    except Exception as e:
        print(f"\n❌ Error: Cannot connect to API at {API_BASE_URL}")
        print(f"   {e}")
        print("\nPlease start the API first:")
        print("  cd /Users/samanb/dev/perceptron/backend")
        print("  python3 app.py\n")
        return 1
    
    try:
        ensure_output_dir()
        generate_daily_files()
        generate_timeseries_files()
        generate_summary()
        
        print("\n" + "="*80)
        print("✅ EXPORT COMPLETE")
        print("="*80)
        print(f"\nFiles saved to: {OUTPUT_DIR.absolute()}")
        print(f"  - Daily keywords:  {OUTPUT_DIR / 'daily'}")
        print(f"  - Time-series:     {OUTPUT_DIR / 'timeseries'}")
        print(f"  - Summary:         {OUTPUT_DIR / 'summary.json'}")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
