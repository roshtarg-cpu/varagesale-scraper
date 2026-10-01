"""VarageSale scraper - extract marketplace listings"""
import re
import json
from datetime import datetime, timezone
from apify import Actor
from camoufox.async_api import AsyncCamoufox


async def main():
    async with Actor:
        # Get input - NO await needed (Actor.get_env() is synchronous in SDK 4.x)
        actor_input = Actor.get_env().get('input', {})
        
        location = actor_input.get('location', 'wichita-ks')
        category = actor_input.get('category', 'all')
        min_price = actor_input.get('minPrice', 0)
        max_price = actor_input.get('maxPrice', 999999)
        max_results = actor_input.get('maxResults', 3)
        proxy_config = actor_input.get('proxyConfiguration', {})
        
        Actor.log.info(f'Starting VarageSale scraper - Location: {location}, Max results: {max_results}')
        
        # Build URL
        base_url = f'https://www.varagesale.com/m/{location}'
        
        Actor.log.info(f'Target URL: {base_url}')
        
        # Get proxy
        proxy_url = None
        if proxy_config.get('useApifyProxy'):
            groups = proxy_config.get('apifyProxyGroups', ['RESIDENTIAL'])
            country = proxy_config.get('apifyProxyCountry', 'US')
            password = f'groups-{"+".join(groups)},country-{country}'
            proxy_url = f'http://auto:{password}@proxy.apify.com:8000'
            Actor.log.info(f'Using proxy: groups={groups}, country={country}')
        
        # Launch browser
        Actor.log.info('Launching browser...')
        async with AsyncCamoufox(
            headless=True,
            proxy=proxy_url
        ) as browser:
            page = await browser.new_page()
            Actor.log.info(f'Navigating to {base_url}')
            await page.goto(base_url, wait_until='networkidle')
            
            # Wait for content
            await page.wait_for_timeout(2000)
            
            # Extract items
            html = await page.content()
            
            # Find all item links
            item_pattern = re.compile(r'href="(/items/[a-z0-9-]+-[a-z0-9-]+)"')
            item_links = list(set(item_pattern.findall(html)))
            
            Actor.log.info(f'Found {len(item_links)} item links')
            
            results_count = 0
            
            for item_path in item_links[:max_results]:
                if results_count >= max_results:
                    break
                
                item_url = f'https://www.varagesale.com{item_path}'
                Actor.log.info(f'Scraping item: {item_url}')
                
                try:
                    await page.goto(item_url, wait_until='networkidle')
                    await page.wait_for_timeout(1000)
                    
                    # Extract JSON-LD data
                    json_ld = await page.evaluate('''
                        () => {
                            const script = document.querySelector('script[type="application/ld+json"]');
                            return script ? script.textContent : null;
                        }
                    ''')
                    
                    if json_ld:
                        data = json.loads(json_ld)
                        
                        # Extract price
                        price_value = data.get('offers', {}).get('price', '0')
                        price_currency = data.get('offers', {}).get('priceCurrency', 'USD')
                        price = f'${price_value} {price_currency}'
                        
                        # Price filtering
                        try:
                            price_num = float(price_value)
                            if price_num < min_price or price_num > max_price:
                                Actor.log.info(f'Skipping {item_url} - price ${price_num} outside range')
                                continue
                        except:
                            pass
                        
                        result = {
                            'url': item_url,
                            'title': data.get('name', None),
                            'description': data.get('description', None),
                            'price': price,
                            'priceValue': price_value,
                            'currency': price_currency,
                            'image': data.get('image', None),
                            'availability': data.get('offers', {}).get('availability', None),
                            'scrapedAt': datetime.now(timezone.utc).isoformat()
                        }
                        
                        await Actor.push_data(result)
                        results_count += 1
                        Actor.log.info(f'Saved: {result["title"]} - {price}')
                    else:
                        Actor.log.warning(f'No JSON-LD data found for {item_url}')
                        await Actor.push_data({
                            'url': item_url,
                            'title': None,
                            'description': None,
                            'price': None,
                            'priceValue': None,
                            'currency': None,
                            'image': None,
                            'availability': None,
                            'scrapedAt': datetime.now(timezone.utc).isoformat()
                        })
                        results_count += 1
                
                except Exception as e:
                    Actor.log.error(f'Error scraping {item_url}: {str(e)}')
                    await Actor.push_data({
                        'url': item_url,
                        'title': None,
                        'description': None,
                        'price': None,
                        'priceValue': None,
                        'currency': None,
                        'image': None,
                        'availability': None,
                        'scrapedAt': datetime.now(timezone.utc).isoformat()
                    })
                    results_count += 1
            
            Actor.log.info(f'Scraper completed - {results_count} items saved')
