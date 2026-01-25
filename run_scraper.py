#!/usr/bin/env python3
"""
iFood Data Scraper - Interactive Mode
Main entry point for the unified scraping workflow

Usage:
    python run_scraper.py --category HOME_FOOD_DELIVERY
    python run_scraper.py --category MERCADO_BEBIDAS --skip-map --skip-headers
"""

import argparse
import sys
import json
import asyncio
import webbrowser
from pathlib import Path
from datetime import datetime


# Category options
AVAILABLE_CATEGORIES = {
    'HOME_FOOD_DELIVERY': 'Restaurantes (delivery de comida)',
    'MERCADO_BEBIDAS': 'Mercados de bebidas',
    'HOME_MERCADO_BR': 'Mercados em geral',
    'MERCADO_FARMACIA': 'Farmácias',
    'MERCADO_PETSHOP': 'Pet shops',
    'SHOPPING_OFICIAL': 'Shopping oficial'
}


def print_header():
    """Print the application header"""
    print("\n" + "=" * 60)
    print("|" + " " * 10 + "iFood Data Scraper - Interactive Mode" + " " * 11 + "|")
    print("=" * 60 + "\n")


def print_step(step_num, total_steps, title):
    """Print a step header"""
    print(f"\n{'-' * 60}")
    print(f"Step {step_num}/{total_steps}: {title}")
    print(f"{'-' * 60}")


def print_success(message):
    """Print a success message"""
    print(f"[+] {message}")


def print_error(message):
    """Print an error message"""
    print(f"[!] {message}")


def print_info(message):
    """Print an info message"""
    print(f" -> {message}")


def select_coordinates(skip_map=False):
    """
    Step 1: Launch coordinate picker and wait for user selection

    Args:
        skip_map: If True, try to load existing coordinates.json

    Returns:
        dict: Coordinates data or None if failed
    """
    print_step(1, 3, "Select Coordinates")

    coordinates_path = Path(__file__).parent / 'coordinates.json'

    # Check if we should skip the map
    if skip_map:
        if coordinates_path.exists():
            print_info("Skipping map, loading existing coordinates...")
            try:
                with open(coordinates_path, 'r', encoding='utf-8') as f:
                    coords_data = json.load(f)
                print_success(f"Loaded {coords_data['count']} coordinates from file")
                return coords_data
            except Exception as e:
                print_error(f"Failed to load coordinates: {e}")
                print_info("Falling back to map selection...")
        else:
            print_error("No existing coordinates.json found")
            print_info("Falling back to map selection...")

    # Import the coordinate picker server
    try:
        from coordinate_picker_server import start_coordinate_picker_server
    except ImportError:
        print_error("Could not import coordinate_picker_server")
        return None

    print_info("Opening coordinate picker in your browser...")
    print_info("Click on the map to select scraping locations")
    print_info("Press Submit when done")
    print()

    # Open browser automatically
    webbrowser.open('http://localhost:8765')

    # Start server and wait for coordinates
    print("[Waiting for coordinate selection...]")
    server, coords_data = start_coordinate_picker_server(port=8765)

    if coords_data:
        print_success(f"Received {coords_data['count']} coordinates")
        return coords_data
    else:
        print_error("No coordinates received")
        return None


def capture_headers(skip_headers=False):
    """
    Step 2: Capture fresh session headers from iFood

    Args:
        skip_headers: If True, try to load existing captured_headers.json

    Returns:
        dict: Headers data or None if failed
    """
    print_step(2, 3, "Capture Headers")

    headers_path = Path(__file__).parent / 'captured_headers.json'

    # Check if we should skip header capture
    if skip_headers:
        if headers_path.exists():
            print_info("Skipping header capture, loading existing headers...")
            try:
                with open(headers_path, 'r', encoding='utf-8') as f:
                    headers_data = json.load(f)
                print_success("Loaded headers from file")
                print_info(f"  - Session ID: {headers_data.get('X-Ifood-Session-Id', 'N/A')[:16]}...")
                print_info(f"  - App Key: {headers_data.get('x-client-application-key', 'N/A')[:16]}...")
                return headers_data
            except Exception as e:
                print_error(f"Failed to load headers: {e}")
                print_info("Falling back to header capture...")
        else:
            print_error("No existing captured_headers.json found")
            print_info("Falling back to header capture...")

    print_info("Opening iFood in browser...")
    print_info("Capturing session headers automatically...")
    print_info("[This may take 15-30 seconds]")
    print()

    try:
        # Import and run header capture
        from capture_ifood_headers import capture_headers_automated

        # Run async function
        headers_data = asyncio.run(capture_headers_automated())

        if headers_data and 'X-Ifood-Session-Id' in headers_data:
            print_success("Headers captured successfully")
            print_info(f"  - Session ID: {headers_data['X-Ifood-Session-Id'][:16]}...")
            print_info(f"  - App Key: {headers_data.get('x-client-application-key', 'N/A')[:16]}...")
            return headers_data
        else:
            print_error("Automatic header capture failed")
            print_info("Trying fallback: using headers from existing scripts...")

            # Fallback: use headers from the original working scripts
            fallback_headers = {
                'X-Ifood-Session-Id': '8d1d8bd8-4382-4eba-a0f9-aec41525b12c',
                'x-client-application-key': '41a266ee-51b7-4c37-9e9d-5cd331f280d5',
                'timestamp': datetime.now().isoformat()
            }

            # Save fallback headers
            with open(headers_path, 'w', encoding='utf-8') as f:
                json.dump(fallback_headers, f, indent=2)

            print_success("Using fallback headers from working scripts")
            print_info("  Note: These headers may expire eventually")
            print_info(f"  - Session ID: {fallback_headers['X-Ifood-Session-Id'][:16]}...")
            print_info(f"  - App Key: {fallback_headers['x-client-application-key'][:16]}...")

            return fallback_headers

    except ImportError:
        print_error("Could not import capture_ifood_headers")
        print_info("Make sure playwright is installed: pip install playwright")
        return None
    except Exception as e:
        print_error(f"Error during header capture: {e}")
        print_info("Using fallback headers...")

        # Use fallback headers even on exception
        fallback_headers = {
            'X-Ifood-Session-Id': '8d1d8bd8-4382-4eba-a0f9-aec41525b12c',
            'x-client-application-key': '41a266ee-51b7-4c37-9e9d-5cd331f280d5',
            'timestamp': datetime.now().isoformat()
        }

        headers_path = Path(__file__).parent / 'captured_headers.json'
        with open(headers_path, 'w', encoding='utf-8') as f:
            json.dump(fallback_headers, f, indent=2)

        print_success("Using fallback headers")
        return fallback_headers


def run_scraper(category, coordinates_data, headers_data):
    """
    Step 3: Run the scraper with selected coordinates and headers

    Args:
        category: Category to scrape (e.g., 'HOME_FOOD_DELIVERY')
        coordinates_data: Dictionary containing coordinates
        headers_data: Dictionary containing captured headers

    Returns:
        bool: True if successful, False otherwise
    """
    print_step(3, 3, "Scraping Data")

    print_info(f"Category: {AVAILABLE_CATEGORIES.get(category, category)}")
    print_info(f"Coordinates: {coordinates_data['count']} locations")
    print()

    try:
        import scraper_core

        # Build full headers
        headers = scraper_core.build_full_headers(headers_data)

        # Load retry attempts
        max_retries = scraper_core.load_retry_attempts(category)

        # Extract coordinates
        coordinates = [(str(c['lat']), str(c['lon'])) for c in coordinates_data['coordinates']]

        # Use first coordinate as default for detail requests
        default_coord = coordinates[0]

        # Step 3.1: Fetch merchant IDs from all locations
        print_info(f"Fetching merchant IDs from {len(coordinates)} locations...")
        all_merchant_ids = []

        for idx, (lat, lon) in enumerate(coordinates, 1):
            print(f"   [{idx}/{len(coordinates)}] Location ({lat}, {lon})...", end='\r')
            merchant_ids = scraper_core.fetch_merchant_ids_from_location(
                category,
                lat,
                lon,
                headers,
                max_retries
            )
            all_merchant_ids.extend(merchant_ids)

        # Deduplicate
        all_merchant_ids = list(set(all_merchant_ids))
        print(f"\n")
        print_success(f"Found {len(all_merchant_ids)} unique merchants")
        print()

        # Step 3.2: Fetch detailed information
        print_info("Fetching detailed merchant information (parallel processing)...")
        merchant_data = scraper_core.fetch_all_merchant_details(
            all_merchant_ids,
            default_coord,
            headers,
            num_workers=3
        )
        print_success(f"Retrieved details for {len(merchant_data)} merchants")
        print()

        # Step 3.3: Export to CSV
        print_info("Generating CSV file...")
        output_file = scraper_core.export_to_csv(merchant_data, category)
        print_success(f"CSV generated: {output_file}")
        print()

        return True

    except ImportError:
        print_error("Could not import scraper_core")
        return False
    except Exception as e:
        print_error(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='iFood Data Scraper - Interactive Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available categories:
  HOME_FOOD_DELIVERY    Restaurantes (delivery de comida)
  MERCADO_BEBIDAS       Mercados de bebidas
  HOME_MERCADO_BR       Mercados em geral
  MERCADO_FARMACIA      Farmácias
  MERCADO_PETSHOP       Pet shops
  SHOPPING_OFICIAL      Shopping oficial

Examples:
  python run_scraper.py --category HOME_FOOD_DELIVERY
  python run_scraper.py --category MERCADO_BEBIDAS --skip-map
  python run_scraper.py --category HOME_MERCADO_BR --skip-map --skip-headers
        """
    )

    parser.add_argument(
        '--category',
        type=str,
        default='HOME_FOOD_DELIVERY',
        choices=list(AVAILABLE_CATEGORIES.keys()),
        help='Category to scrape (default: HOME_FOOD_DELIVERY)'
    )

    parser.add_argument(
        '--skip-map',
        action='store_true',
        help='Skip coordinate selection and use existing coordinates.json'
    )

    parser.add_argument(
        '--skip-headers',
        action='store_true',
        help='Skip header capture and use existing captured_headers.json'
    )

    args = parser.parse_args()

    # Print header
    print_header()

    # Step 1: Select coordinates
    coordinates_data = select_coordinates(skip_map=args.skip_map)
    if not coordinates_data:
        print_error("Failed to get coordinates. Exiting.")
        sys.exit(1)

    # Step 2: Capture headers
    headers_data = capture_headers(skip_headers=args.skip_headers)
    if not headers_data:
        print_error("Failed to capture headers. Exiting.")
        sys.exit(1)

    # Step 3: Run scraper
    success = run_scraper(args.category, coordinates_data, headers_data)

    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("|" + " " * 18 + "Scraping Complete!" + " " * 19 + "|")
    else:
        print("|" + " " * 15 + "Scraping Not Yet Implemented" + " " * 15 + "|")
    print("=" * 60 + "\n")

    if not success:
        print_info("Next step: Implement scraper_core.py")

    input("\nPress ENTER to exit...")


if __name__ == '__main__':
    main()
