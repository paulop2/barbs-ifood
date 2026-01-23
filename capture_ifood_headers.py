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
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # Listen for requests to marketplace.ifood.com.br
        async def handle_request(request):
            if 'marketplace.ifood.com.br' in request.url:
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
        await page.goto('https://www.ifood.com.br', wait_until='networkidle')

        print("\nWaiting for marketplace requests...")
        # Wait a bit for any automatic requests
        await page.wait_for_timeout(3000)

        # If we haven't captured headers yet, try to trigger a search
        if not captured_headers:
            print("\nTrying to trigger a search...")
            try:
                # Look for a search box or location input
                await page.wait_for_timeout(2000)

                # Try to click on search or location
                search_selectors = [
                    'input[placeholder*="endereço"]',
                    'input[type="text"]',
                    'button:has-text("Endereço")',
                ]

                for selector in search_selectors:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            await element.click(timeout=2000)
                            await page.wait_for_timeout(2000)
                            break
                    except:
                        continue

                # Wait for potential API calls
                await page.wait_for_timeout(5000)

            except Exception as e:
                print(f"Note: {e}")

        if captured_headers:
            print("\n" + "="*60)
            print("SUCCESS! Headers captured:")
            print("="*60)
            print(f"\nX-Ifood-Session-Id: {captured_headers.get('X-Ifood-Session-Id', 'NOT FOUND')}")
            print(f"x-client-application-key: {captured_headers.get('x-client-application-key', 'NOT FOUND')}")
            print("\n" + "="*60)

            # Save to file
            with open('captured_headers.json', 'w') as f:
                json.dump(captured_headers, f, indent=2)
            print("Headers saved to: captured_headers.json")
        else:
            print("\n[!] No headers captured yet. The browser will stay open.")
            print("Please manually:")
            print("  1. Enter your location")
            print("  2. Browse restaurants")
            print("  3. Wait for headers to be captured")
            print("\nPress Ctrl+C in the terminal when done to save headers...")

            # Keep browser open and wait
            try:
                await page.wait_for_timeout(300000)  # Wait 5 minutes
            except:
                pass

        # Keep browser open for a moment so user can see
        await page.wait_for_timeout(5000)
        await browser.close()

        return captured_headers

if __name__ == '__main__':
    headers = asyncio.run(capture_headers())

    if headers:
        print("\n[+] Done! Use these headers in your script.")
    else:
        print("\n[!] Could not capture headers automatically.")
        print("You may need to manually browse iFood to trigger API requests.")
