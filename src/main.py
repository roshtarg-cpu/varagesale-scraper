"""Geebo classifieds scraper"""
import re
import json
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from apify import Actor


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        
        category = input_data.get('category', 'all')
        location = input_data.get('location', 'usa')
        max_results = input_data.get('maxResults', 10)
        
        print(f'[INFO] Geebo scraper started - category: {category}, location: {location}, max: {max_results}', flush=True)
        
        try:
            # Build URL
            if category == 'all':
                base_url = 'https://geebo.com'
            else:
                base_url = f'https://geebo.com/{category}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            print(f'[INFO] Fetching {base_url}', flush=True)
            
            resp = requests.get(base_url, headers=headers, timeout=30)
            print(f'[INFO] Response: status={resp.status_code}, len={len(resp.text)}', flush=True)
            
            if resp.status_code != 200:
                print(f'[ERROR] Non-200 status: {resp.status_code}', flush=True)
                return
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find listing links - Geebo uses class="gtitle"
            listing_links = []
            for link in soup.find_all('a', class_='gtitle'):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    listing_links.append(full_url)
            
            # Limit results
            listing_links = listing_links[:max_results]
            print(f'[INFO] Found {len(listing_links)} listings', flush=True)
            
            results_count = 0
            for listing_url in listing_links:
                print(f'[INFO] Scraping {listing_url}', flush=True)
                
                try:
                    listing_resp = requests.get(listing_url, headers=headers, timeout=30)
                    
                    if listing_resp.status_code != 200:
                        print(f'[WARN] Non-200 for {listing_url}: {listing_resp.status_code}', flush=True)
                        continue
                    
                    listing_soup = BeautifulSoup(listing_resp.text, 'html.parser')
                    
                    # Extract data
                    title = listing_soup.find('h1', class_='page-title')
                    title_text = title.get_text(strip=True) if title else None
                    
                    description_div = listing_soup.find('div', class_='description')
                    description = description_div.get_text(strip=True) if description_div else None
                    
                    # Price - usually in the title or separate element
                    price = None
                    price_elem = listing_soup.find('span', class_='price')
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                    
                    # Location
                    location_elem = listing_soup.find('span', class_='location')
                    location_text = location_elem.get_text(strip=True) if location_elem else None
                    
                    # Image
                    image = None
                    img_tag = listing_soup.find('img', class_='main-image')
                    if img_tag:
                        image = img_tag.get('src')
                    
                    result = {
                        'url': listing_url,
                        'title': title_text,
                        'description': description,
                        'price': price,
                        'location': location_text,
                        'image': image,
                        'category': category,
                        'scrapedAt': datetime.now(timezone.utc).isoformat()
                    }
                    
                    await Actor.push_data(result)
                    results_count += 1
                    print(f'[SUCCESS] Saved: {title_text}', flush=True)
                    
                except Exception as e:
                    print(f'[ERROR] Error scraping {listing_url}: {e}', flush=True)
            
            print(f'[DONE] Scraper completed - {results_count}/{len(listing_links)} items saved', flush=True)
            
        except Exception as e:
            print(f'[FATAL] Fatal error: {e}', flush=True)
            import traceback
            traceback.print_exc()
            raise
