from scrapers.amazon import AmazonScraper
from tools import DatabaseManager
import asyncio
import time
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_caching():
    query = "wireless mouse"
    db = DatabaseManager()

    print(f"--- 1. First Run (Live Parsing) for '{query}' ---")
    start = time.time()

    # Simulate what the agent does: Scrape then Cache
    # We just run one scraper for test speed, the agent runs all
    async def _run_scrape():
        s = AmazonScraper()
        return await s.search(query)

    results = asyncio.run(_run_scrape())

    print(f"Scraped {len(results)} items in {time.time() - start:.2f}s")

    if results:
        print("Caching results...")
        db.cache_results(query, results)

    print(f"\n--- 2. Second Run (Cache Retrieval) for '{query}' ---")
    start = time.time()
    cached = db.get_cached_results(query)

    if cached:
        print(f"✅ Cache Hit! Retrieved {len(cached)} items in {time.time() - start:.2f}s")
        print("Sample Item:", cached[0]['title'])
    else:
        print("❌ Cache Miss (Failed to store or retrieve)")


if __name__ == "__main__":
    test_caching()
