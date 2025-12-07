import asyncio
import logging
import sys

# Windows Loop Policy Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from price_tracker import PriceTracker
from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper
from scrapers.ebay import EbayScraper

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_daily_scan():
    print("🚀 Starting Daily Price Monitor...")
    
    tracker = PriceTracker()
    
    # Initialize Scrapers
    scrapers = {
        "Amazon": AmazonScraper(),
        "Flipkart": FlipkartScraper(),
        "eBay": EbayScraper(),
        # "Walmart": WalmartScraper()
    }
    
    # Run Scan
    updated_count = await tracker.scan_all(scrapers)
    
    print(f"✅ Monitor Complete!")
    print(f"📊 Updated {updated_count} products with fresh prices.")
    print("💡 Check 'data/price_history.json' for the new log.")

if __name__ == "__main__":
    try:
        asyncio.run(run_daily_scan())
    except Exception as e:
        print(f"❌ Scan Failed: {e}")
