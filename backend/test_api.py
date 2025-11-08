import requests

try:
    response = requests.get('http://localhost:8000/api/reputation/map', timeout=10)
    print(f'Status: {response.status_code}')
    data = response.json()
    print(f'Data points: {len(data.get("data", []))}')
    if data.get('data'):
        print('Sample data point:')
        print(data['data'][0])
except Exception as e:
    print(f'Error: {e}')