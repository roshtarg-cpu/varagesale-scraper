"""VarageSale scraper with Playwright"""
from datetime import datetime, timezone
from apify import Actor
from playwright.async_api import async_playwright


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        
        location = input_data.get('location', 'toronto')
        max_results = input_data.get('maxResults', 10)
        
        print(f'[INFO] VarageSale scraper - location: {location}, max: {max_results}', flush=True)
        
        async with async_playwright() as p:
            print('[INFO] Launching browser...', flush=True)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            url = f'https://www.varagesale.com/m/{location}'
            print(f'[INFO] Loading {url}', flush=True)
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                print('[INFO] Page loaded', flush=True)
                
                # Wait for listings
                await page.wait_for_selector('a[href*="/items/"]', timeout=10000)
                
                # Extract links
                links = await page.eval_on_selector_all(
                    'a[href*="/items/"]',
                    '(elements) => elements.map(e => e.href)'
                )
                
                unique_links = list(set(links))[:max_results]
                print(f'[INFO] Found {len(unique_links)} listings', flush=True)
                
                for listing_url in unique_links:
                    print(f'[INFO] Scraping {listing_url}', flush=True)
                    
                    try:
                        await page.goto(listing_url, wait_until='domcontentloaded', timeout=30000)
                        
                        # Extract JSON-LD
                        json_ld = await page.eval_on_selector(
                            'script[type="application/ld+json"]',
                            'el => JSON.parse(el.textContent)'
                        )
                        
                        result = {
                            'url': listing_url,
                            'title': json_ld.get('name'),
                            'description': json_ld.get('description'),
                            'price': json_ld.get('offers', {}).get('price'),
                            'currency': json_ld.get('offers', {}).get('priceCurrency', 'USD'),
                            'image': json_ld.get('image'),
                            'scrapedAt': datetime.now(timezone.utc).isoformat()
                        }
                        
                        await Actor.push_data(result)
                        print(f'[SUCCESS] Saved: {result["title"]}', flush=True)
                        
                    except Exception as e:
                        print(f'[WARN] Failed {listing_url}: {e}', flush=True)
                
                print(f'[DONE] Completed - {len(unique_links)} listings', flush=True)
                
            except Exception as e:
                print(f'[ERROR] {e}', flush=True)
                import traceback
                traceback.print_exc()
                raise
            finally:
                await browser.close()
