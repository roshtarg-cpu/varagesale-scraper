"""Classifieds scraper - DEMO with sample data

NOTE: Real classified sites (VarageSale, Geebo, Hoobly, Recycler) have:
- Cloudflare/bot protection (403)  
- JavaScript SPAs (no static HTML)
- Require browser automation + residential proxies

This demo shows working actor structure with sample listings.
"""

import json
from datetime import datetime, timezone
from apify import Actor


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        
        category = input_data.get('category', 'all')
        max_results = input_data.get('maxResults', 10)
        
        Actor.log.info(f'Classifieds scraper - category: {category}, max: {max_results}')
        Actor.log.warning('DEMO VERSION: Returns sample data. Real sites need browser automation.')
        
        samples = [
            {'title': 'Honda Civic 2018', 'price': '$15,500', 'category': 'vehicles', 'location': 'Chicago, IL'},
            {'title': 'iPhone 14 Pro', 'price': '$899', 'category': 'electronics', 'location': 'Austin, TX'},
            {'title': 'Sofa 3-Seater', 'price': '$350', 'category': 'furniture', 'location': 'Seattle, WA'},
            {'title': 'Trek Mountain Bike', 'price': '$650', 'category': 'sporting', 'location': 'Denver, CO'},
            {'title': '2BR Apartment', 'price': '$1,800/mo', 'category': 'housing', 'location': 'Portland, OR'},
        ]
        
        for i, item in enumerate(samples[:max_results], 1):
            item.update({
                'url': f'https://example.com/listing/{i}',
                'image': 'https://via.placeholder.com/400x300',
                'scrapedAt': datetime.now(timezone.utc).isoformat(),
                'note': 'Sample data - upgrade to Playwright for real scraping'
            })
            await Actor.push_data(item)
        
        Actor.log.info(f'Returned {min(len(samples), max_results)} sample listings')
