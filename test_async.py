import asyncio
import time
import logging
import sys
from agent import ShoppingAgent

# Windows Loop Policy Fix for aiohttp
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO)

async def test_performance():
    agent = ShoppingAgent()
    query = "gaming headset"
    
    print(f"--- Testing Async Performance for '{query}' ---")
    start = time.time()
    
    # We call the async method directly to test
    results = await agent.search_online_async(query)
    
    duration = time.time() - start
    print(f"\n✅ Completed in {duration:.2f} seconds")
    print(f"📦 Found {len(results)} products")
    
    for p in results[:3]:
        print(f" - [{p['source']}] {p['title'][:40]}... ${p['price']}")

if __name__ == "__main__":
    asyncio.run(test_performance())
