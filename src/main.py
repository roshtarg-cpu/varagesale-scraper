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
        proxy_config = input_data.get('proxyConfiguration')
        
        print(f'[INFO] VarageSale scraper started - location: {location}, maxResults: {max_results}', flush=True)
        
        # Get proxy URL from Apify
        proxy_url = None
        if proxy_config:
            print(f'[INFO] Using proxy configuration', flush=True)
            proxy_info = await Actor.create_proxy_configuration(proxy_config)
            if proxy_info:
                proxy_url = await proxy_info.new_url()
                print(f'[INFO] Proxy URL obtained', flush=True)
        
        proxies = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
        
        try:
            # Fetch main page
            base_url = f'https://www.varagesale.com/m/{location}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            print(f'[INFO] Fetching {base_url}', flush=True)
            
            try:
                resp = requests.get(base_url, headers=headers, proxies=proxies, timeout=30)
                print(f'[INFO] Got response: status={resp.status_code}, len={len(resp.text)}', flush=True)
                
                if resp.status_code == 403:
                    print(f'[ERROR] 403 Forbidden - site blocking requests', flush=True)
                    print(f'[ERROR] Response preview: {resp.text[:500]}', flush=True)
                    return
                
                html = resp.text
            except Exception as e:
                print(f'[ERROR] Request failed: {e}', flush=True)
                raise
            
            # Find item links
            item_pattern = re.compile(r'href="(/items/[a-z0-9-]+-[a-z0-9-]+)"')
            item_links = list(set(item_pattern.findall(html)))[:max_results]
            
            print(f'[INFO] Found {len(item_links)} item links', flush=True)
            
            results_count = 0
            for item_path in item_links:
                item_url = f'https://www.varagesale.com{item_path}'
                print(f'[INFO] Scraping {item_url}', flush=True)
                
                try:
                    item_resp = requests.get(item_url, headers=headers, proxies=proxies, timeout=30)
                    
                    if item_resp.status_code != 200:
                        print(f'[WARN] Non-200 status: {item_resp.status_code}', flush=True)
                        continue
                    
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
            import traceback
            traceback.print_exc()
            raise
