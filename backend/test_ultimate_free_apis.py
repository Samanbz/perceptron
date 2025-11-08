import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from reputation_apis import RedditAPI, GitHubAPI, SocialMediaPresenceAPI, ReputationDataAggregator
import json

print('Testing NEW ULTIMATE FREE reputation APIs...\n')

# Test Reddit API
print('1. Reddit Community Discussions - 100% FREE:')
reddit_api = RedditAPI()
try:
    reddit_data = reddit_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(reddit_data)} data points')
    for item in reddit_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test GitHub API
print('\n2. GitHub Open Source Activity - 100% FREE:')
github_api = GitHubAPI()
try:
    github_data = github_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(github_data)} data points')
    for item in github_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test Social Media API
print('\n3. Social Media Presence - 100% FREE:')
social_api = SocialMediaPresenceAPI()
try:
    social_data = social_api.fetch_reputation_data('Apple Inc.', 'United States')
    print(f'   Found {len(social_data)} data points')
    for item in social_data[:1]:
        print(f'   - {item.title}: {item.severity} risk')
        print(f'     {item.description}')
except Exception as e:
    print(f'   Error: {e}')

# Test the full aggregator with all sources
print('\n4. FULL AGGREGATOR TEST (ALL 12 free sources):')
aggregator = ReputationDataAggregator()
try:
    all_data = aggregator.fetch_all_reputation_data('Apple Inc.', 'United States')
    print(f'   Total data points from ALL free sources: {len(all_data)}')
    print('   Sources included:')
    for i, data in enumerate(all_data[:12]):
        print(f'   {i+1}. {data.sources[0]}')
except Exception as e:
    print(f'   Error: {e}')

print('\n✅ All new ultimate free APIs tested!')