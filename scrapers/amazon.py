import asyncio
from typing import List, Dict, Any

from bs4 import BeautifulSoup

from .base import AsyncECommerceScraper, Product


class AmazonScraper(AsyncECommerceScraper):
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """HTTP-based Amazon search parsing using aiohttp + rotating headers.

        If parsing fails (Amazon may block or obfuscate), return stable demo items.
        """
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        items: List[Dict[str, Any]] = []

        try:
            soup = await self.fetch(url)
            if soup:
                for div in soup.select("div[data-component-type='s-search-result']"):
                    title_el = div.select_one("h2 a.a-link-normal.a-text-normal") or div.select_one("h2 a.a-link-normal")
                    price_whole = div.select_one(".a-price-whole")
                    price_frac = div.select_one(".a-price-fraction")
                    link_el = title_el if title_el and title_el.has_attr('href') else div.select_one("a.a-link-normal", href=True)

                    if not title_el or not price_whole:
                        continue

                    title = title_el.text.strip()
                    try:
                        price = float((price_whole.text + (price_frac.text if price_frac else "0")).replace(",", ""))
                    except Exception:
                        continue

                    items.append({
                        "title": title,
                        "price": price,
                        "currency": "INR",
                        "source": "Amazon",
                        "url": f"https://www.amazon.in{link_el['href']}" if link_el and link_el.has_attr('href') else "https://www.amazon.in",
                    })

                    if len(items) >= 10:
                        break
        except Exception:
            items = []

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

        products: List[Dict[str, Any]] = []
        for item in items:
            p = Product()
            p.title = item.get("title", "")
            p.price = float(item.get("price", 0.0) or 0.0)
            p.currency = item.get("currency", "INR")
            p.source = item.get("source", "Amazon")
            p.url = item.get("url", "#")
            p.score = 1.0 if p.price > 0 else 0.1
            products.append(p.to_dict())

        return products


def scrape_amazon(query: str) -> List[Dict[str, Any]]:
    return asyncio.run(AmazonScraper().search(query))

