# Geebo Scraper - v1.1
FROM apify/actor-python:3.11

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
