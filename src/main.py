"""VarageSale scraper with Playwright"""
import asyncio
from urllib.parse import urljoin
from datetime import datetime, timezone
from apify import Actor
from playwright.async_api import async_playwright


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        
        location = input_data.get('location', 'toronto')
        max_results = input_data.get('maxResults', 10)
        
        Actor.log.info(f'VarageSale scraper - location: {location}, max: {max_results}')
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Navigate to location
            url = f'https://www.varagesale.com/m/{location}'
            Actor.log.info(f'Loading {url}')
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                Actor.log.info(f'Page loaded')
                
                # Wait for listings to load
                await page.wait_for_selector('a[href*="/items/"]', timeout=10000)
                
                # Extract listing links
                links = await page.eval_on_selector_all(
                    'a[href*="/items/"]',
                    '(elements) => elements.map(e => e.href)'
                )
                
                Actor.log.info(f'Found {len(links)} listings')
                
                unique_links = list(set(links))[:max_results]
                
                for listing_url in unique_links:
                    Actor.log.info(f'Scraping {listing_url}')
                    
                    try:
                        await page.goto(listing_url, wait_until='domcontentloaded', timeout=30000)
                        
                        # Extract JSON-LD data
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
                        Actor.log.info(f'✓ Saved: {result["title"]}')
                        
                    except Exception as e:
                        Actor.log.warning(f'Failed to scrape {listing_url}: {e}')
                
                Actor.log.info(f'Completed - scraped {len(unique_links)} listings')
                
            except Exception as e:
                Actor.log.error(f'Error: {e}')
                raise
            finally:
                await browser.close()
