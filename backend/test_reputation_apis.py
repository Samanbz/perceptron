#!/usr/bin/env python3
"""
Test script for reputation APIs integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from reputation_apis import reputation_aggregator
import asyncio

async def test_reputation_apis():
    """Test the reputation APIs with sample data"""

    print("🧪 Testing Reputation APIs Integration")
    print("=" * 50)

    # Test companies
    test_cases = [
        ("Apple", "United States"),
        ("Microsoft", "United States"),
        ("Google", "United States")
    ]

    for company, country in test_cases:
        print(f"\n📊 Testing {company} in {country}")
        print("-" * 30)

        try:
            # Fetch reputation data
            reputation_data = reputation_aggregator.fetch_all_reputation_data(company, country)

            print(f"✅ Fetched {len(reputation_data)} reputation items")

            # Display sample data
            for i, data in enumerate(reputation_data[:3]):  # Show first 3 items
                print(f"  {i+1}. {data.title}")
                print(f"     Risk Type: {data.risk_type}")
                print(f"     Severity: {data.severity}")
                print(f"     Sentiment: {data.sentiment:.2f}")
                print(f"     Sources: {', '.join(data.sources)}")
                print()

        except Exception as e:
            print(f"❌ Error testing {company}: {e}")

    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_reputation_apis())