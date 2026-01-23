import requests
from urllib.parse import urlparse
import json
import re

# Try to get headers from iFood
session = requests.Session()

# First, visit the main page to establish a session
print("Visiting iFood main page...")
response = session.get('https://www.ifood.com.br', verify=False)
print(f"Status: {response.status_code}")

# Try to make a request to the marketplace API and see what happens
url = 'https://marketplace.ifood.com.br/v2/home'
params = {
    'latitude': '-23.48511167789553',
    'longitude': '-46.352385881847496',
    'channel': 'IFOOD',
    'size': '10',
    'alias': 'HOME_FOOD_DELIVERY'
}

headers = {
    'Host': 'marketplace.ifood.com.br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.ifood.com.br/',
    'Origin': 'https://www.ifood.com.br',
}

print("\nTrying to access marketplace API...")
response = session.post(url, headers=headers, json={
    "supported-headers": ["OPERATION_HEADER"],
    "supported-cards": ["MERCHANT_LIST"],
}, verify=False)

print(f"Status: {response.status_code}")
print(f"\nResponse headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\nRequest headers sent:")
for key, value in response.request.headers.items():
    print(f"  {key}: {value}")

if response.status_code != 200:
    print(f"\nResponse body: {response.text[:500]}")
