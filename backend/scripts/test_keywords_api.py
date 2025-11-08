#!/usr/bin/env python3
"""
Test the Keywords API endpoints integrated into app.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app import app

def test_api():
    """Test all keyword API endpoints."""
    
    print("\n" + "="*80)
    print("TESTING KEYWORDS API (Integrated into app.py)")
    print("="*80 + "\n")
    
    client = TestClient(app)
    
    # 1. Health check
    print("1️⃣  Testing /api/health")
    print("-" * 80)
    response = client.get('/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 2. Get teams
    print("2️⃣  Testing /api/teams")
    print("-" * 80)
    response = client.get('/api/teams')
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Teams found: {data['count']}")
    for team in data['teams']:
        print(f"  - {team['team_name']} ({team['team_key']})")
    print()
    
    # 3. Get statistics
    print("3️⃣  Testing /api/keywords/stats")
    print("-" * 80)
    response = client.get('/api/keywords/stats')
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total keywords: {data['total_keywords']}")
    print(f"Date range: {data['date_range']['start']} to {data['date_range']['end']}")
    print(f"\nBy team:")
    for item in data['by_team']:
        print(f"  {item['team']:15s} | {item['count']:4d} keywords")
    print(f"\nBy date:")
    for item in data['by_date'][:5]:
        print(f"  {item['date']} | {item['count']:3d} keywords")
    print()
    
    # 4. Get keywords for a specific date
    print("4️⃣  Testing /api/keywords?date=2025-11-02")
    print("-" * 80)
    response = client.get('/api/keywords?date=2025-11-02&limit=10')
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Date: {data['date']}")
    print(f"Keywords found: {data['count']}")
    print(f"\nTop 10 keywords:")
    for i, kw in enumerate(data['keywords'][:10], 1):
        print(f"  {i:2d}. {kw['keyword']:25s} | {kw['team_key']:12s} | score: {kw['importance_score']:5.2f}")
    print()
    
    # 5. Get keywords for specific team and date
    print("5️⃣  Testing /api/keywords?date=2025-11-02&team=researcher&limit=5")
    print("-" * 80)
    response = client.get('/api/keywords?date=2025-11-02&team=researcher&limit=5')
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Date: {data['date']}, Team: {data['team']}")
    print(f"Keywords found: {data['count']}")
    print(f"\nTop 5 keywords for researcher team:")
    for i, kw in enumerate(data['keywords'], 1):
        print(f"  {i}. {kw['keyword']:25s}")
        print(f"     Importance: {kw['importance_score']:5.2f}")
        print(f"     Sentiment: {kw['sentiment']['score']:+.3f} (pos:{kw['sentiment']['positive']} neg:{kw['sentiment']['negative']} neu:{kw['sentiment']['neutral']})")
        print(f"     Metrics: freq={kw['metrics']['frequency']}, docs={kw['metrics']['document_count']}")
        if kw['sample_snippets']:
            snippet_text = kw['sample_snippets'][0].get('text', '')[:80]
            print(f"     Sample: \"{snippet_text}...\"")
        print()
    
    # 6. Search keywords
    print("6️⃣  Testing /api/keywords/search?q=ai")
    print("-" * 80)
    response = client.get('/api/keywords/search?q=ai&limit=5')
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Query: '{data['query']}'")
    print(f"Results found: {data['count']}")
    for i, result in enumerate(data['results'], 1):
        print(f"  {i}. {result['keyword']:25s} | {result['team_key']:12s} | max_score: {result['max_score']}")
    print()
    
    # 7. Test with invalid date
    print("7️⃣  Testing error handling (invalid date)")
    print("-" * 80)
    response = client.get('/api/keywords?date=invalid')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    print("="*80)
    print("✅ API TESTING COMPLETE")
    print("="*80 + "\n")
    
    print("📚 API Documentation available at:")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/redoc")
    print()


if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
