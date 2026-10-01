"""VarageSale scraper"""
import re
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from apify import Actor


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        
        location = input_data.get('location', 'wichita-ks')
        max_results = input_data.get('maxResults', 3)
        
        print(f'[INFO] VarageSale scraper started - location: {location}, maxResults: {max_results}', flush=True)
        
        try:
            # Fetch main page
            base_url = f'https://www.varagesale.com/m/{location}'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            print(f'[INFO] Fetching {base_url}', flush=True)
            
            try:
                resp = requests.get(base_url, headers=headers, timeout=30)
                print(f'[INFO] Got response: status={resp.status_code}, len={len(resp.text)}', flush=True)
                html = resp.text
            except Exception as e:
                print(f'[ERROR] Request failed: {e}', flush=True)
                raise
            
            # Find item links
            item_pattern = re.compile(r'href="(/items/[a-z0-9-]+-[a-z0-9-]+)"')
            item_links = list(set(item_pattern.findall(html)))[:max_results]
            
            print(f'[INFO] Found {len(item_links)} item links: {item_links}', flush=True)
            
            results_count = 0
            for item_path in item_links:
                item_url = f'https://www.varagesale.com{item_path}'
                print(f'[INFO] Scraping {item_url}', flush=True)
                
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
                        print(f'[SUCCESS] Saved: {result["title"]}', flush=True)
                    else:
                        print(f'[WARN] No JSON-LD found on {item_url}', flush=True)
                except Exception as e:
                    print(f'[ERROR] Error scraping {item_url}: {e}', flush=True)
            
            print(f'[DONE] Scraper completed - {results_count} items saved', flush=True)
            
        except Exception as e:
            print(f'[FATAL] Fatal error: {e}', flush=True)
            raise
