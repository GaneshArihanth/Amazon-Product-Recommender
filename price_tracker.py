import json
import os
import datetime
import logging
import asyncio
from price_history_provider import PriceHistoryProvider
# We import scrapers dynamically or pass them in to avoid circular imports if possible, 
# or just import here if structure allows.
# For simplicity in this project structure, we will rely on external injection or lazy import.

logger = logging.getLogger(__name__)

class PriceTracker:
    def __init__(self, data_file_path=None, external_provider=None):
        if data_file_path is None:
            self.data_file_path = os.path.join(os.getcwd(), 'data', 'price_history.json')
        else:
            self.data_file_path = data_file_path
            
        self.external_provider = external_provider
            
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.data_file_path):
            directory = os.path.dirname(self.data_file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.data_file_path, 'w') as f:
                json.dump({"tracked_items": {}}, f, indent=2)

    def _load(self):
        try:
            with open(self.data_file_path, 'r') as f:
                return json.load(f)
        except: return {"tracked_items": {}}

    def _save(self, data):
        with open(self.data_file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def track_item(self, sku, url, title, current_price, currency, source=None):
        """Register an item for tracking and log price point."""
        if current_price <= 0: return # Don't track invalid prices

        data = self._load()
        today = datetime.date.today().isoformat()
        
        # Unique ID: Use URL as stable ID
        item_id = url 
        
        if item_id not in data['tracked_items']:
            data['tracked_items'][item_id] = {
                "title": title,
                "url": url,
                "currency": currency,
                "source": source if source else "",
                "history": []
            }
            
        history = data['tracked_items'][item_id]['history']
        
        # Add history point if tracking for the first time today
        if not history or history[-1]['date'] != today:
            history.append({
                "date": today,
                "price": current_price
            })
            # Keep history clean: maybe limit to 365 days? 
            # For college project, unlimited is fine.
            
        self._save(data)

    def get_forecast(self, url):
        """
        Analyze long-term trends (up to 30 days).
        Returns advice string.
        """
        # Prefer external history provider if it has advice
        try:
            if self.external_provider:
                external = self.external_provider.get_advice(url)
                if external:
                    return external
        except Exception:
            pass

        data = self._load()
        item = data['tracked_items'].get(url)
        if not item or len(item['history']) < 2:
            return "🆕 New Item: collecting data..."
            
        history = item['history']
        latest_price = history[-1]['price']
        
        # 1. Check Short Term (Yesterday vs Today)
        prev_price = history[-2]['price']
        if latest_price < prev_price:
            drop_pct = ((prev_price - latest_price) / prev_price) * 100
            if drop_pct > 20:
                return f"🔥 FIRE DEAL: Dropped {drop_pct:.1f}%!"
            return f"📉 Price Drop: Down {drop_pct:.1f}% (Buy Now)"
            
        if latest_price > prev_price:
            return "📈 Price Rising: Wait (Was cheaper recently)"
            
        # 2. Check Long Term (30 Day Avg)
        # Get prices from last 30 entries
        prices = [p['price'] for p in history[-30:]]
        avg_price = sum(prices) / len(prices)
        
        if latest_price < avg_price * 0.95: # 5% below average
            return f"✅ Good Deal: 5% below monthly average."
            
        return "➡️ Price Stable: Monitor for drops."

    async def scan_all(self, scrapers_map):
        """
        Background Task: Re-scrapes all tracked items to update their history.
        scrapers_map: Dict of {Source: ScraperInstance}
        """
        data = self._load()
        items = data.get('tracked_items', {})
        logger.info(f"PriceTracker: Scanning {len(items)} items...")
        
        updates = 0
        tasks = []
        
        for url, info in items.items():
            # Identify source
            scraper = None
            if "amazon" in url: scraper = scrapers_map.get("Amazon")
            elif "flipkart" in url: scraper = scrapers_map.get("Flipkart")
            elif "ebay" in url: scraper = scrapers_map.get("eBay")
            # Fallback to stored source if URL does not contain hints (e.g., synthetic IDs)
            if not scraper:
                src = (info or {}).get("source", "")
                if src in scrapers_map:
                    scraper = scrapers_map.get(src)
            
            if scraper:
                # We need a scraper method that takes a direct URL, or we search by Title as fallback?
                # Most scrapers built so far are 'Search' based. 
                # Ideally we need `scrape_product_page(url)`.
                # For this project, to avoid complexity, we key off the 'Title' and re-search.
                # (Re-searching is safer as page parsing validation is hard).
                tasks.append(self._update_item_by_search(scraper, info['title'], url))
                
        if tasks:
            results = await asyncio.gather(*tasks)
            updates = sum(results)
            
        return updates

    async def _update_item_by_search(self, scraper, title, origin_url):
        try:
            # Re-search the title
            results = await scraper.search(title)
            # Find the matching item (heuristically matches URL or assume top result)
            # Simple heuristic: Top result
            if results:
                best = results[0]
                self.track_item(None, origin_url, best['title'], best['price'], best['currency'])
                return 1
        except Exception as e:
            logger.error(f"Failed update for {title}: {e}")
        return 0
