import requests
import urllib3
import warnings

warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

LATITUDE_PESQUISA = "-23.48511167789553"
LONGITUDE_PESQUISA = "-46.352385881847496"

HEADERS = {
    'Host': 'cw-marketplace.ifood.com.br',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not(A:Brand";v="24", "Chromium";v="122"',
    'app_version': '9.102.44',
    'browser': 'Windows',
    'accept-language': 'pt-BR,pt;q=1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'x-client-application-key': '41a266ee-51b7-4c37-9e9d-5cd331f280d5',
    'Accept': 'application/json, text/plain, */*',
    'Cache-Control': 'no-cache, no-store',
    'X-Ifood-Session-Id': '8d1d8bd8-4382-4eba-a0f9-aec41525b12c',
    'x-device-model': 'Windows Chrome',
    'platform': 'Desktop',
    'sec-ch-ua-platform': '"Windows"',
    'Origin': 'https://www.ifood.com.br',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.ifood.com.br/',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
}

URL = f'https://cw-marketplace.ifood.com.br/v2/home?latitude={LATITUDE_PESQUISA}&longitude={LONGITUDE_PESQUISA}&channel=IFOOD&size=100&alias=HOME_FOOD_DELIVERY'

PAYLOAD = {
    "supported-headers": ["OPERATION_HEADER"],
    "supported-cards": ["MERCHANT_LIST", "CATALOG_ITEM_LIST", "CATALOG_ITEM_LIST_V2", "CATALOG_ITEM_LIST_V3",
                        "FEATURED_MERCHANT_LIST", "CATALOG_ITEM_CAROUSEL", "CATALOG_ITEM_CAROUSEL_V2",
                        "CATALOG_ITEM_CAROUSEL_V3", "BIG_BANNER_CAROUSEL", "IMAGE_BANNER",
                        "MERCHANT_LIST_WITH_ITEMS_CAROUSEL", "SMALL_BANNER_CAROUSEL", "NEXT_CONTENT",
                        "MERCHANT_CAROUSEL", "MERCHANT_TILE_CAROUSEL", "SIMPLE_MERCHANT_CAROUSEL", "INFO_CARD",
                        "MERCHANT_LIST_V2", "ROUND_IMAGE_CAROUSEL", "BANNER_GRID", "MEDIUM_IMAGE_BANNER",
                        "MEDIUM_BANNER_CAROUSEL", "RELATED_SEARCH_CAROUSEL", "ADS_BANNER"],
    "supported-actions": ["catalog-item", "merchant", "page", "card-content", "last-restaurants",
                          "webmiddleware", "reorder", "search", "groceries", "home-tab"],
    "feed-feature-name": "", "faster-overrides": ""
}

print("Making request to iFood API...")
print(f"URL: {URL}")
print(f"\nHeaders:")
for key, value in HEADERS.items():
    print(f"  {key}: {value}")

response = requests.post(URL, headers=HEADERS, json=PAYLOAD, verify=False)

print(f"\n\nResponse Status Code: {response.status_code}")
print(f"Response Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\n\nResponse Body (first 1000 chars):")
print(response.text[:1000])

if response.status_code == 200:
    try:
        json_data = response.json()
        print(f"\n\nJSON parsed successfully!")
        print(f"Keys in response: {list(json_data.keys())}")
    except:
        print("\n\nFailed to parse JSON")
