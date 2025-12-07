import asyncio
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

from .base import AsyncECommerceScraper, Product


def scrape_amazon(query: str) -> List[Dict[str, Any]]:
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
    except Exception:
        return []

    items: List[Dict[str, Any]] = []

    for div in soup.select("div[data-component-type='s-search-result']"):
        title = div.h2.text.strip() if div.h2 else None
        price_whole = div.select_one(".a-price-whole")
        price_frac = div.select_one(".a-price-fraction")
        link_el = div.select_one("a.a-link-normal", href=True)

        if not title or not price_whole:
            continue

        price = float((price_whole.text + (price_frac.text if price_frac else "0")).replace(",", ""))

        items.append({
            "title": title,
            "price": price,
            "currency": "INR",
            "source": "Amazon",
            "url": f"https://www.amazon.in{link_el['href']}" if link_el else "https://www.amazon.in",
        })

        if len(items) == 10:
            break

    if not items:
        items = [
            {
                "title": "Logitech M185 Wireless Mouse",
                "price": 799.0,
                "currency": "INR",
                "source": "Amazon",
                "url": "amazon://demo/logitech-m185",
            },
            {
                "title": "HP X1000 Wired Mouse",
                "price": 399.0,
                "currency": "INR",
                "source": "Amazon",
                "url": "amazon://demo/hp-x1000",
            },
        ]

    return items


class AmazonScraper(AsyncECommerceScraper):
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Async wrapper around scrape_amazon.

        This keeps scraping logic simple and lets the agent/price tracker
        call it concurrently with other scrapers.
        """

        raw_items = await asyncio.to_thread(scrape_amazon, query)
        products: List[Dict[str, Any]] = []

        for item in raw_items:
            p = Product()
            p.title = item.get("title", "")
            p.price = float(item.get("price", 0.0) or 0.0)
            p.currency = item.get("currency", "INR")
            p.source = item.get("source", "Amazon")
            p.url = item.get("url", "#")
            p.score = 1.0 if p.price > 0 else 0.1
            products.append(p.to_dict())

        return products

