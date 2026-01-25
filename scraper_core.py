"""
iFood Data Scraper Core Module

This module contains the core scraping logic extracted from the original scripts.
It provides reusable functions for fetching merchant data from iFood's API.
"""

import time
import json
import requests
import pandas as pd
import urllib3
import warnings
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from multiprocessing import Pool, Manager

warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    # Fallback progress indicator
    class tqdm:
        def __init__(self, iterable=None, total=None, desc=None, **kwargs):
            self.iterable = iterable
            self.total = total or (len(iterable) if iterable else 0)
            self.desc = desc
            self.n = 0

        def __iter__(self):
            for item in self.iterable:
                yield item
                self.update(1)

        def update(self, n=1):
            self.n += n
            if self.total > 0:
                pct = (self.n / self.total) * 100
                print(f"\r{self.desc}: {self.n}/{self.total} ({pct:.1f}%)", end='', flush=True)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            print()  # New line after progress

# Category structure: Maps category name to (section_idx, card_idx) in API response
CATEGORY_STRUCTURE = {
    "HOME_FOOD_DELIVERY": (1, 0),
    "MERCADO_BEBIDAS": (0, 4),
    "HOME_MERCADO_BR": (0, 5),
    "MERCADO_FARMACIA": (0, 6),
    "MERCADO_PETSHOP": (0, 5),
    "SHOPPING_OFICIAL": (0, 5)
}


def load_coordinates(filepath='coordinates.json') -> List[Tuple[str, str]]:
    """
    Load coordinates from JSON file

    Args:
        filepath: Path to coordinates JSON file

    Returns:
        List of (latitude, longitude) tuples
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        coordinates = []
        for coord in data.get('coordinates', []):
            lat = str(coord['lat'])
            lon = str(coord['lon'])
            coordinates.append((lat, lon))

        return coordinates
    except Exception as e:
        print(f"Error loading coordinates: {e}")
        return []


def load_headers(filepath='captured_headers.json') -> Dict[str, str]:
    """
    Load captured headers from JSON file

    Args:
        filepath: Path to headers JSON file

    Returns:
        Dictionary of captured headers
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading headers: {e}")
        return {}


def build_full_headers(captured_headers: dict) -> dict:
    """
    Build complete headers dictionary with captured session data

    Args:
        captured_headers: Dict with X-Ifood-Session-Id and x-client-application-key

    Returns:
        Complete headers dict for API requests
    """
    base_headers = {
        'Host': 'cw-marketplace.ifood.com.br',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not(A:Brand";v="24", "Chromium";v="122"',
        'app_version': '9.102.44',
        'browser': 'Windows',
        'accept-language': 'pt-BR,pt;q=1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Cache-Control': 'no-cache, no-store',
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

    # Override with captured headers
    if 'X-Ifood-Session-Id' in captured_headers:
        base_headers['X-Ifood-Session-Id'] = captured_headers['X-Ifood-Session-Id']
    if 'x-client-application-key' in captured_headers:
        base_headers['x-client-application-key'] = captured_headers['x-client-application-key']

    return base_headers


def load_retry_attempts(category='HOME_FOOD_DELIVERY') -> int:
    """
    Load retry attempts from TENTATIVAS.txt

    Args:
        category: Category being scraped (determines which directory to check)

    Returns:
        Number of retry attempts (default: 5)
    """
    try:
        # Try to load from appropriate directory
        if category == 'HOME_FOOD_DELIVERY':
            tentativas_path = Path(__file__).parent / 'restaurantes' / 'TENTATIVAS.txt'
        else:
            tentativas_path = Path(__file__).parent / 'outras categorias' / 'TENTATIVAS.txt'

        if tentativas_path.exists():
            with open(tentativas_path, 'r') as f:
                return int(f.read().strip())
    except:
        pass

    return 5  # Default fallback


def fetch_merchant_ids_from_location(
    category_alias: str,
    latitude: str,
    longitude: str,
    headers: dict,
    max_retries: int = 5
) -> List[str]:
    """
    Fetch merchant IDs from a single location

    Args:
        category_alias: Category to fetch (e.g., 'HOME_FOOD_DELIVERY')
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        headers: Request headers
        max_retries: Maximum retry attempts for pagination

    Returns:
        List of merchant IDs
    """
    merchant_ids = []

    try:
        url = f'https://cw-marketplace.ifood.com.br/v2/home?latitude={latitude}&longitude={longitude}&channel=IFOOD&size=100&alias={category_alias}'

        payload = {
            "supported-headers": ["OPERATION_HEADER"],
            "supported-cards": [
                "MERCHANT_LIST", "CATALOG_ITEM_LIST", "CATALOG_ITEM_LIST_V2", "CATALOG_ITEM_LIST_V3",
                "FEATURED_MERCHANT_LIST", "CATALOG_ITEM_CAROUSEL", "CATALOG_ITEM_CAROUSEL_V2",
                "CATALOG_ITEM_CAROUSEL_V3", "BIG_BANNER_CAROUSEL", "IMAGE_BANNER",
                "MERCHANT_LIST_WITH_ITEMS_CAROUSEL", "SMALL_BANNER_CAROUSEL", "NEXT_CONTENT",
                "MERCHANT_CAROUSEL", "MERCHANT_TILE_CAROUSEL", "SIMPLE_MERCHANT_CAROUSEL", "INFO_CARD",
                "MERCHANT_LIST_V2", "ROUND_IMAGE_CAROUSEL", "BANNER_GRID", "MEDIUM_IMAGE_BANNER",
                "MEDIUM_BANNER_CAROUSEL", "RELATED_SEARCH_CAROUSEL", "ADS_BANNER"
            ],
            "supported-actions": [
                "catalog-item", "merchant", "page", "card-content", "last-restaurants",
                "webmiddleware", "reorder", "search", "groceries", "home-tab"
            ],
            "feed-feature-name": "",
            "faster-overrides": ""
        }

        # Initial request
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        section_idx, card_idx = CATEGORY_STRUCTURE[category_alias]

        # Extract initial IDs
        for content in response.json()['sections'][section_idx]['cards'][card_idx]['data']['contents']:
            merchant_ids.append(content['id'])

        # Try to get cursor for pagination
        try:
            cursor = str(response.json()['sections'][section_idx]['cards'][card_idx + 1]['data']['action']).split('cursor=')[1]
        except:
            return merchant_ids

        section_id = str(response.json()['sections'][section_idx]['id'])

        # Pagination loop
        retry_count = 0
        while True:
            time.sleep(1)  # Rate limiting

            try:
                paginated_url = f'https://cw-marketplace.ifood.com.br/v2/home?latitude={latitude}&longitude={longitude}&channel=IFOOD&size=100&section={section_id}&cursor={cursor}&alias={category_alias}'
                response = requests.post(paginated_url, headers=headers, json=payload, verify=False, timeout=30)

                contents = response.json()['sections'][section_idx]['cards'][card_idx]['data']['contents']
                cursor = str(response.json()['sections'][section_idx]['cards'][card_idx + 1]['data']['action']).split('cursor=')[1]
                section_id = str(response.json()['sections'][section_idx]['id'])

                for content in contents:
                    merchant_ids.append(content['id'])

                retry_count = 0  # Reset on success

            except:
                retry_count += 1
                if retry_count >= max_retries:
                    break

        return merchant_ids

    except Exception as e:
        print(f"Error fetching IDs from location ({latitude}, {longitude}): {e}")
        return merchant_ids


def fetch_merchant_details(
    merchant_id: str,
    latitude: str,
    longitude: str,
    headers: dict
) -> Optional[Dict]:
    """
    Fetch detailed information for a single merchant

    Args:
        merchant_id: Merchant ID to fetch
        latitude: Latitude for the request
        longitude: Longitude for the request
        headers: Request headers

    Returns:
        Dictionary with merchant details or None if failed
    """
    try:
        url = f'https://cw-marketplace.ifood.com.br/v1/merchant-info/graphql?latitude={latitude}&longitude={longitude}&channel=IFOOD'

        payload = {
            "query": "query ($merchantId: String!) { merchant (merchantId: $merchantId, required: true) { available availableForScheduling contextSetup { catalogGroup context regionGroup } currency deliveryFee { originalValue type value } deliveryMethods { catalogGroup deliveredBy id maxTime minTime mode originalValue priority schedule { now shifts { dayOfWeek endTime interval startTime } timeSlots { availableLoad date endDateTime endTime id isAvailable originalPrice price startDateTime startTime } } subtitle title type value state } deliveryTime distance features id mainCategory { code name } minimumOrderValue name paymentCodes preparationTime priceRange resources { fileName type } slug tags takeoutTime userRating } merchantExtra (merchantId: $merchantId, required: false) { address { city country district latitude longitude state streetName streetNumber timezone zipCode } categories { code description friendlyName } companyCode configs { bagItemNoteLength chargeDifferentToppingsMode nationalIdentificationNumberRequired orderNoteLength } deliveryTime description documents { CNPJ { type value } MCC { type value } } enabled features groups { externalId id name type } id locale mainCategory { code description friendlyName } merchantChain { externalId id name } metadata { ifoodClub { banner { action image priority title } } } minimumOrderValue name phoneIf priceRange resources { fileName type } shifts { dayOfWeek duration start } shortId tags takeoutTime test type userRatingCount } }",
            "variables": {"merchantId": merchant_id}
        }

        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        data = response.json()['data']

        merchant = data.get('merchant', {})
        merchant_extra = data.get('merchantExtra', {})
        address = merchant_extra.get('address', {})
        documents = merchant_extra.get('documents', {})
        cnpj = documents.get('CNPJ', {})

        # Check for super restaurant tag
        tags = merchant_extra.get('tags', [])
        is_super = "SIM" if "SUPER_RESTAURANT" in tags else "NAO"

        # Convert price range
        price_range = merchant.get('priceRange', '')
        price_display = {
            "CHEAPEST": "$",
            "CHEAP": "$$",
            "MODERATE": "$$$",
            "EXPENSIVE": "$$$$",
            "MOST_EXPENSIVE": "$$$$$"
        }.get(price_range, price_range)

        return {
            "NOME": merchant.get('name', ''),
            "RUA": address.get('streetName', ''),
            "NUMERO": address.get('streetNumber', ''),
            "BAIRRO": address.get('district', ''),
            "CIDADE": address.get('city', ''),
            "CEP": address.get('zipCode', ''),
            "LATITUDE": address.get('latitude', ''),
            "LONGITUDE": address.get('longitude', ''),
            "CNPJ": cnpj.get('value', ''),
            "PRECO MEDIO": price_display,
            "VALOR MINIMO": merchant_extra.get('minimumOrderValue', ''),
            "CATEGORIA": merchant.get('mainCategory', {}).get('name', ''),
            "AVALIACAO": merchant.get('userRating', ''),
            "TEMPO ENTREGA": merchant.get('deliveryTime', ''),
            "VALOR ORIGINAL": merchant.get('deliveryFee', {}).get('originalValue', ''),
            "SUPER RESTAURANTE": is_super,
        }

    except:
        return None


def worker_fetch_details(params):
    """Worker function for multiprocessing pool"""
    merchant_id, latitude, longitude, headers, results_list, counter, lock = params
    result = fetch_merchant_details(merchant_id, latitude, longitude, headers)
    if result:
        results_list.append(result)

    # Update progress counter
    with lock:
        counter.value += 1


def fetch_all_merchant_details(
    merchant_ids: List[str],
    default_coordinates: Tuple[str, str],
    headers: dict,
    num_workers: int = 3
) -> List[Dict]:
    """
    Fetch details for all merchants using parallel processing

    Args:
        merchant_ids: List of merchant IDs to fetch
        default_coordinates: (lat, lon) tuple for detail requests
        headers: Request headers
        num_workers: Number of parallel workers

    Returns:
        List of merchant detail dictionaries
    """
    manager = Manager()
    results_list = manager.list()
    counter = manager.Value('i', 0)
    lock = manager.Lock()

    params_list = [
        (mid, default_coordinates[0], default_coordinates[1], headers, results_list, counter, lock)
        for mid in merchant_ids
    ]

    print(f"   Processing {len(merchant_ids)} merchants with {num_workers} workers...")

    with Pool(processes=num_workers) as pool:
        # Use imap_unordered for better progress tracking
        for _ in pool.imap_unordered(worker_fetch_details, params_list):
            # Print progress (using ASCII for Windows compatibility)
            current = counter.value
            total = len(merchant_ids)
            pct = (current / total) * 100 if total > 0 else 0
            bar_length = 40
            filled = int(bar_length * current / total) if total > 0 else 0
            bar = '#' * filled + '-' * (bar_length - filled)
            print(f"\r   [{bar}] {current}/{total} ({pct:.1f}%)", end='', flush=True)

    print()  # New line after progress
    return list(results_list)


def export_to_csv(data: List[Dict], category: str, output_dir: Path = None) -> str:
    """
    Export merchant data to CSV file

    Args:
        data: List of merchant data dictionaries
        category: Category name for the output file
        output_dir: Directory to save the CSV (default: current directory)

    Returns:
        Path to the created CSV file
    """
    if output_dir is None:
        output_dir = Path.cwd()

    columns = [
        "NOME", "RUA", "NUMERO", "BAIRRO", "CIDADE", "CEP",
        "LATITUDE", "LONGITUDE", "CNPJ", "PRECO MEDIO",
        "VALOR MINIMO", "CATEGORIA", "AVALIACAO",
        "TEMPO ENTREGA", "VALOR ORIGINAL", "SUPER RESTAURANTE"
    ]

    df = pd.DataFrame(data, columns=columns)
    output_file = output_dir / f"RESULTADO {category.upper()} IFOOD.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    return str(output_file)
