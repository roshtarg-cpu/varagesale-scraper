"""VarageSale scraper with Playwright stealth"""
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
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ]
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/Toronto'
            )
            
            # Remove webdriver flag
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)
            
            page = await context.new_page()
            
            url = f'https://www.varagesale.com/m/{location}'
            print(f'[INFO] Loading {url}', flush=True)
            
            try:
                await page.goto(url, wait_until='load', timeout=60000)
                await page.wait_for_timeout(3000)  # Let JS load
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
                        await page.goto(listing_url, wait_until='load', timeout=30000)
                        await page.wait_for_timeout(2000)
                        
                        # Extract from HTML
                        title = await page.text_content('h1')
                        
                        price = None
                        for selector in ['.price', '[class*="price"]', 'span:has-text("$")']:
                            try:
                                price = await page.text_content(selector, timeout=2000)
                                if price and '$' in price:
                                    break
                            except:
                                pass
                        
                        description = None
                        for selector in ['.description', '[class*="description"]', 'p']:
                            try:
                                description = await page.text_content(selector, timeout=2000)
                                if description and len(description) > 20:
                                    break
                            except:
                                pass
                        
                        image = None
                        try:
                            image = await page.get_attribute('img', 'src', timeout=2000)
                        except:
                            pass
                        
                        result = {
                            'url': listing_url,
                            'title': title.strip() if title else None,
                            'description': description.strip() if description else None,
                            'price': price.strip() if price else None,
                            'image': image,
                            'location': location,
                            'scrapedAt': datetime.now(timezone.utc).isoformat()
                        }
                        
                        await Actor.push_data(result)
                        print(f'[SUCCESS] Saved: {result["title"]}', flush=True)
                        
                    except Exception as e:
                        print(f'[WARN] Failed {listing_url}: {e}', flush=True)
                
                print(f'[DONE] Completed - scraped {len(unique_links)} listings', flush=True)
                
            except Exception as e:
                print(f'[ERROR] {e}', flush=True)
                import traceback
                traceback.print_exc()
                raise
            finally:
                await browser.close()
