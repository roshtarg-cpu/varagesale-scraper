# VarageSale Scraper with Playwright
FROM apify/actor-python:3.11-playwright

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . ./
