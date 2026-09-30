# 🔍 VarageSale Scraper - AI-Powered Marketplace Data Extraction

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-00D4FF?style=flat-square)](https://apify.com/fervent_bus/varagesale-scraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![AI Agent Compatible](https://img.shields.io/badge/AI-Claude%20%7C%20ChatGPT%20%7C%20MCP-blueviolet?style=flat-square)](https://apify.com)

Extract structured data from **VarageSale** marketplace with this powerful scraper. Built for developers, AI agents (Claude, ChatGPT), and automation workflows via **Apify MCP integration**.

---

## ✨ Features

- 🤖 **AI Agent Ready** - Works seamlessly with Claude, ChatGPT, and other AI agents via Apify MCP
- 🔄 **Full Pagination** - Automatically scrapes all available listings
- 🌍 **Location Filtering** - Target specific cities and regions
- 💰 **Price Range Filters** - Filter by minimum and maximum price
- 📊 **Multiple Export Formats** - JSON, CSV, Excel, HTML
- ⚡ **Fast & Reliable** - Optimized for speed and accuracy with browser automation
- 🛡️ **Anti-Bot Protection** - Handles protection with Camoufox browser
- 🔍 **Category Support** - Filter by furniture, electronics, clothing, toys, and more

---

## 🚀 Quick Start

### Via Apify Console
1. Go to [Apify Console](https://console.apify.com/actors/fervent_bus~varagesale-scraper)
2. Configure input fields (location, price range, etc.)
3. Click **Run** and download results

### Via API (Python)
```python
from apify_client import ApifyClient

client = ApifyClient('YOUR_APIFY_TOKEN')

run = client.actor('fervent_bus/varagesale-scraper').call(run_input={
    'location': 'wichita-ks',
    'minPrice': 0,
    'maxPrice': 500,
    'maxResults': 50,
})

# Fetch results
items = client.dataset(run['defaultDatasetId']).list_items().items
for item in items:
    print(f"{item['title']} - {item['price']}")
```

### Via API (JavaScript)
```javascript
const ApifyClient = require('apify-client');

const client = new ApifyClient({ token: 'YOUR_APIFY_TOKEN' });

const run = await client.actor('fervent_bus/varagesale-scraper').call({
    location: 'new-york-ny',
    minPrice: 0,
    maxPrice: 1000,
    maxResults: 50,
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();
items.forEach(item => console.log(`${item.title} - ${item.price}`));
```

### Via cURL
```bash
curl -X POST https://api.apify.com/v2/acts/fervent_bus~varagesale-scraper/runs \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location": "wichita-ks", "maxResults": 50}'
```

---

## 📥 Input Configuration

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| `location` | String | City/region slug (e.g., 'wichita-ks', 'new-york-ny') | ❌ | wichita-ks |
| `category` | String | Filter by category (all, furniture, electronics, etc.) | ❌ | all |
| `minPrice` | Integer | Minimum price filter (0 for no limit) | ❌ | 0 |
| `maxPrice` | Integer | Maximum price filter (999999 for no limit) | ❌ | 999999 |
| `maxResults` | Integer | Maximum results to scrape (default: 3) | ❌ | 3 |
| `proxyConfiguration` | Object | Proxy settings (RESIDENTIAL group recommended) | ❌ | RESIDENTIAL |

---

## 📤 Output Structure

```json
[
  {
    "url": "https://www.varagesale.com/items/abc123-recliner",
    "title": "Recliner",
    "description": "Comfortable recliner in good condition",
    "price": "$80 USD",
    "priceValue": "80",
    "currency": "USD",
    "image": "https://pixl.varagesale.com/...",
    "availability": "http://schema.org/InStock",
    "scrapedAt": "2026-09-25T14:30:00.000Z"
  }
]
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `url` | String | Direct link to the listing |
| `title` | String | Listing title |
| `description` | String | Full listing description |
| `price` | String | Formatted price with currency |
| `priceValue` | String | Numeric price value |
| `currency` | String | Price currency (USD, EUR, etc.) |
| `image` | String | Main listing image URL |
| `availability` | String | Product availability status |
| `scrapedAt` | String | ISO timestamp when data was collected |

---

## 💡 Use Cases

### 🎯 Lead Generation
Extract contact information and seller details for sales outreach and market intelligence.

### 📊 Market Research
Monitor competitor pricing, product trends, and inventory levels in local marketplaces.

### 💰 Price Monitoring
Set up automated price tracking for specific items or categories across different regions.

### 🤖 AI Agent Workflows
Integrate with **Claude Code**, **ChatGPT plugins**, or custom AI agents via **Apify MCP** for automated data collection and analysis workflows.

### 📈 Business Intelligence
Aggregate marketplace data for strategic decision-making, demand forecasting, and trend analysis.

### 🏠 Local Market Analysis
Track local marketplace activity, pricing patterns, and product availability in specific cities.

---

## ❓ FAQ

### Does it handle pagination?
Yes! The scraper automatically follows pagination and collects all available results up to your `maxResults` limit.

### Can I use proxies?
Absolutely. We recommend using **RESIDENTIAL** proxy group for best results. Configure via `proxyConfiguration` input.

### What export formats are supported?
JSON, CSV, Excel (XLSX), HTML, RSS, and XML. Download from Apify Console or fetch via API.

### Is it compatible with AI agents?
✅ **Yes!** This actor works with **Claude Code**, **ChatGPT**, and other AI agents through **Apify MCP integration**. Use it directly from your AI assistant for automated marketplace research.

### How often can I run it?
As often as you need! Runs are limited only by your Apify subscription plan.

### Does it bypass anti-bot protection?
Yes, we use **Camoufox** browser with fingerprinting, residential proxies, and adaptive strategies to handle protection systems.

### Can I filter by location?
Yes! Use the `location` parameter with city/region slugs like 'new-york-ny', 'los-angeles-ca', 'chicago-il', etc.

---

## 💰 Pricing

| Event Type | Price | Description |
|------------|-------|-------------|
| 💵 **Per Result** | $0.005 | Each listing/item scraped |
| 🚀 **Actor Start** | $0.05 | One-time fee per run |

**Example:** Scraping 100 results = $0.05 (start) + $0.50 (100 × $0.005) = **$0.55 total**

[View detailed pricing](https://apify.com/fervent_bus/varagesale-scraper/pricing)

---

## 🔗 Links

- 🏠 [Actor Page](https://apify.com/fervent_bus/varagesale-scraper)
- 📚 [Apify Documentation](https://docs.apify.com)
- 💬 [Support](https://console.apify.com/actors/fervent_bus~varagesale-scraper/issues)
- 🐙 [GitHub Repository](https://github.com/roshtarg-cpu/varagesale-scraper)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ for developers and AI agents. Compatible with Claude, ChatGPT & AI automation via Apify MCP.**
