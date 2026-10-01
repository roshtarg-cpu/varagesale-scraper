"""VarageSale scraper - minimal version"""
import re
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from apify import Actor


async def main():
    print("main() called", flush=True)
    
    async with Actor:
        print("Inside Actor context", flush=True)
        
        input_data = await Actor.get_input() or {}
        print(f"Got input: {input_data}", flush=True)
        
        location = input_data.get('location', 'wichita-ks')
        max_results = input_data.get('maxResults', 3)
        
        Actor.log.info(f'VarageSale scraper started - location: {location}, maxResults: {max_results}')
        
        try:
            # Fetch main page
            base_url = f'https://www.varagesale.com/m/{location}'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            Actor.log.info(f'Fetching {base_url}')
            resp = requests.get(base_url, headers=headers, timeout=30)
            html = resp.text
            
            # Find item links
            item_pattern = re.compile(r'href="(/items/[a-z0-9-]+-[a-z0-9-]+)"')
            item_links = list(set(item_pattern.findall(html)))[:max_results]
            
            Actor.log.info(f'Found {len(item_links)} item links')
            
            results_count = 0
            for item_path in item_links:
                item_url = f'https://www.varagesale.com{item_path}'
                Actor.log.info(f'Scraping {item_url}')
                
                try:
                    item_resp = requests.get(item_url, headers=headers, timeout=30)
                    soup = BeautifulSoup(item_resp.text, 'html.parser')
                    
                    json_ld_tag = soup.find('script', {'type': 'application/ld+json'})
                    
                    if json_ld_tag:
                        data = json.loads(json_ld_tag.string)
                        result = {
                            'url': item_url,
                            'title': data.get('name'),
                            'description': data.get('description'),
                            'price': data.get('offers', {}).get('price'),
                            'currency': data.get('offers', {}).get('priceCurrency', 'USD'),
                            'image': data.get('image'),
                            'scrapedAt': datetime.now(timezone.utc).isoformat()
                        }
                        await Actor.push_data(result)
                        results_count += 1
                        Actor.log.info(f'✓ Saved: {result["title"]}')
                except Exception as e:
                    Actor.log.error(f'Error scraping {item_url}: {e}')
            
            Actor.log.info(f'Scraper completed - {results_count} items saved')
            print(f"Done! {results_count} items", flush=True)
            
        except Exception as e:
            Actor.log.error(f'Fatal error: {e}')
            print(f"FATAL: {e}", flush=True)
            raise
