import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GITHUB_API_KEY')
print(f'API Key loaded: {api_key is not None}')

headers = {
    'User-Agent': 'PerceptronReputationBot/1.0',
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {api_key}'
}

# Test different search queries
test_queries = [
    'org:netflix',
    'user:netflix',
    'netflix in:name',
    'tensorflow',  # Known to exist
    'kubernetes'   # Known to exist
]

for query in test_queries:
    print(f"\nTesting query: '{query}'")
    url = 'https://api.github.com/search/repositories'
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 3
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(f'Status Code: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        total_count = data.get("total_count", 0)
        print(f'Total repositories found: {total_count}')

        items = data.get('items', [])
        print(f'Items returned: {len(items)}')

        if items:
            for item in items[:2]:
                full_name = item.get("full_name", "Unknown")
                stars = item.get("stargazers_count", 0)
                print(f'- {full_name}: {stars} stars')
    else:
        print(f'Error: {response.status_code}')