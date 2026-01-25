import asyncio
from playwright.async_api import async_playwright
import json

async def capture_headers():
    captured_headers = {}

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            geolocation={'latitude': -23.5505, 'longitude': -46.6333},  # São Paulo coordinates
            permissions=['geolocation']
        )
        page = await context.new_page()

        # Listen for requests to marketplace.ifood.com.br
        async def handle_request(request):
            if 'marketplace.ifood.com.br' in request.url or 'cw-marketplace.ifood.com.br' in request.url:
                headers = await request.all_headers()
                if 'x-ifood-session-id' in headers:
                    captured_headers['X-Ifood-Session-Id'] = headers['x-ifood-session-id']
                if 'x-client-application-key' in headers:
                    captured_headers['x-client-application-key'] = headers['x-client-application-key']

                print(f"\n[+] Captured request to: {request.url[:80]}...")
                if 'X-Ifood-Session-Id' in captured_headers and 'x-client-application-key' in captured_headers:
                    print(f"\n[+] X-Ifood-Session-Id: {captured_headers['X-Ifood-Session-Id']}")
                    print(f"[+] x-client-application-key: {captured_headers['x-client-application-key']}")

        page.on('request', handle_request)

        print("Opening iFood website...")
        await page.goto('https://www.ifood.com.br', wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)

        print("\nAutomatically entering São Paulo address...")

        # Strategy 1: Try to navigate directly to a location-specific URL
        try:
            # Navigate to São Paulo with coordinates
            sao_paulo_url = 'https://www.ifood.com.br/delivery/sao-paulo-sp'
            print(f"Navigating to: {sao_paulo_url}")
            await page.goto(sao_paulo_url, wait_until='domcontentloaded')
            await page.wait_for_timeout(5000)

            if 'X-Ifood-Session-Id' in captured_headers and 'x-client-application-key' in captured_headers:
                print("\n[+] Headers captured from navigation!")
            else:
                # Try scrolling to trigger lazy-loaded content
                print("Scrolling page to trigger API calls...")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)

        except Exception as e:
            print(f"Navigation attempt failed: {e}")

        # Strategy 2: Try finding and filling address input
        if not (captured_headers.get('X-Ifood-Session-Id') and captured_headers.get('x-client-application-key')):
            print("\nTrying to find address input...")
            try:
                # Common selectors for iFood address input
                address_selectors = [
                    'input[placeholder*="Rua"]',
                    'input[placeholder*="endereço"]',
                    'input[placeholder*="CEP"]',
                    'input[type="text"]',
                    'input[data-test-id*="address"]',
                ]

                for selector in address_selectors:
                    try:
                        input_field = page.locator(selector).first
                        if await input_field.is_visible(timeout=2000):
                            print(f"Found input field: {selector}")
                            await input_field.click()
                            await page.wait_for_timeout(1000)
                            # Type a São Paulo address
                            await input_field.fill("Avenida Paulista, 1578, São Paulo")
                            await page.wait_for_timeout(2000)

                            # Press Enter or look for submit button
                            await input_field.press('Enter')
                            await page.wait_for_timeout(5000)
                            break
                    except:
                        continue

            except Exception as e:
                print(f"Address input attempt failed: {e}")

        # Strategy 3: Direct API call simulation
        if not (captured_headers.get('X-Ifood-Session-Id') and captured_headers.get('x-client-application-key')):
            print("\nTrying direct marketplace URL...")
            try:
                # Navigate to a direct marketplace endpoint that should trigger the API
                marketplace_url = 'https://www.ifood.com.br/delivery/sao-paulo-sp/restaurantes'
                await page.goto(marketplace_url, wait_until='domcontentloaded')
                await page.wait_for_timeout(8000)

                # Scroll to load more content
                for i in range(3):
                    await page.evaluate("window.scrollBy(0, 500)")
                    await page.wait_for_timeout(2000)

            except Exception as e:
                print(f"Marketplace URL attempt failed: {e}")

        # Final check
        if captured_headers.get('X-Ifood-Session-Id') and captured_headers.get('x-client-application-key'):
            print("\n" + "="*60)
            print("SUCCESS! Headers captured:")
            print("="*60)
            print(f"\nX-Ifood-Session-Id: {captured_headers['X-Ifood-Session-Id']}")
            print(f"x-client-application-key: {captured_headers['x-client-application-key']}")
            print("\n" + "="*60)

            # Save to file
            with open('captured_headers.json', 'w') as f:
                json.dump(captured_headers, f, indent=2)
            print("Headers saved to: captured_headers.json")
        else:
            print("\n[!] Could not capture headers automatically.")
            print("The browser will stay open for manual intervention...")
            print("\nPlease:")
            print("  1. Enter your location")
            print("  2. Browse restaurants")
            print("  3. Wait for headers to be captured")
            print("\nPress Ctrl+C when done...")

            # Keep browser open and wait
            try:
                await page.wait_for_timeout(300000)  # Wait 5 minutes
            except:
                pass

        # Keep browser open briefly
        await page.wait_for_timeout(3000)
        await browser.close()

        return captured_headers


async def capture_headers_automated():
    """
    Automated header capture function for integration with main script

    Returns:
        dict: Captured headers with X-Ifood-Session-Id and x-client-application-key
              Returns empty dict if capture fails
    """
    try:
        headers = await capture_headers()
        if headers and 'X-Ifood-Session-Id' in headers and 'x-client-application-key' in headers:
            # Save to file with timestamp
            import json
            from datetime import datetime

            headers['timestamp'] = datetime.now().isoformat()

            with open('captured_headers.json', 'w') as f:
                json.dump(headers, f, indent=2)

            return headers
        else:
            return {}
    except Exception as e:
        print(f"\n[!] Error during header capture: {e}")
        return {}


if __name__ == '__main__':
    headers = asyncio.run(capture_headers())

    if headers:
        print("\n[+] Done! Use these headers in your script.")
    else:
        print("\n[!] Could not capture headers automatically.")
        print("You may need to manually browse iFood to trigger API requests.")
