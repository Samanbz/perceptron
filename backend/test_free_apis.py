import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from reputation_apis import BBBAPI, TrustpilotAPI, GooglePlayStoreAPI, AppleAppStoreAPI, WHOISAPI, RSSNewsAPI, ReputationDataAggregator
import json

print('Testing ENHANCED COMPLETELY FREE reputation APIs (no keys required)...\n')

# Test BBB API (completely free, no key)
print('1. Better Business Bureau (BBB) - 100% FREE:')
bbb_api = BBBAPI()
try:
    bbb_data = bbb_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(bbb_data)} data points')
    for item in bbb_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test Trustpilot API (completely free, no key)
print('\n2. Trustpilot Reviews - 100% FREE:')
tp_api = TrustpilotAPI()
try:
    tp_data = tp_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(tp_data)} data points')
    for item in tp_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test Google Play Store API (completely free, no key)
print('\n3. Google Play Store Reviews - 100% FREE:')
gp_api = GooglePlayStoreAPI()
try:
    gp_data = gp_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(gp_data)} data points')
    for item in gp_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test Apple App Store API (completely free, no key)
print('\n4. Apple App Store Reviews - 100% FREE:')
as_api = AppleAppStoreAPI()
try:
    as_data = as_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(as_data)} data points')
    for item in as_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test WHOIS API (completely free, no key)
print('\n5. WHOIS Domain Registration - 100% FREE:')
whois_api = WHOISAPI()
try:
    whois_data = whois_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(whois_data)} data points')
    for item in whois_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test RSS News API (completely free, no key)
print('\n6. RSS News Feeds - 100% FREE:')
rss_api = RSSNewsAPI()
try:
    rss_data = rss_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(rss_data)} data points')
    for item in rss_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test the full aggregator with all free sources
print('\n7. FULL AGGREGATOR TEST (ALL 9 free sources):')
aggregator = ReputationDataAggregator()
try:
    all_data = aggregator.fetch_all_reputation_data('Apple Inc.', 'United States')
    print(f'   Total data points from ALL free sources: {len(all_data)}')
    for i, data in enumerate(all_data[:5]):
        print(f'   {i+1}. {data.sources[0]}: {data.title} ({data.severity} risk)')
except Exception as e:
    print(f'   Error: {e}')

print('\n✅ All enhanced free APIs tested!')