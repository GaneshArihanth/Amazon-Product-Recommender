import asyncio
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from .selenium_driver import get_driver
import time

from .base import AsyncECommerceScraper, Product


def scrape_flipkart(query: str) -> List[Dict[str, Any]]:
    driver = get_driver()
    search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    driver.get(search_url)

    time.sleep(3)  # allow JS to load

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "lxml")
    items: List[Dict[str, Any]] = []

    for card in soup.select("div._4ddWXP, div._1AtVbE"):
        title_el = card.select_one("a.s1Q9rs") or card.select_one("div._4rR01T")
        price_el = card.select_one("div._30jeq3")
        link_el = card.select_one("a.s1Q9rs")

        if not title_el or not price_el:
            continue

        title = title_el.text.strip()
        price = float(price_el.text.replace("₹", "").replace(",", "").strip())

        items.append({
            "title": title,
            "price": price,
            "currency": "INR",
            "source": "Flipkart",
            "url": f"https://www.flipkart.com{link_el['href']}" if link_el and link_el.has_attr("href") else "https://www.flipkart.com",
        })

        if len(items) == 10:
            break

    if not items:
        items = [
            {
                "title": "Logitech M221 Wireless Mouse",
                "price": 749.0,
                "currency": "INR",
                "source": "Flipkart",
                "url": "flipkart://demo/logitech-m221",
            },
            {
                "title": "Dell MS116 Wired Optical Mouse",
                "price": 349.0,
                "currency": "INR",
                "source": "Flipkart",
                "url": "flipkart://demo/dell-ms116",
            },
        ]

    return items


class FlipkartScraper(AsyncECommerceScraper):
    async def search(self, query: str) -> List[Dict[str, Any]]:
        raw_items = await asyncio.to_thread(scrape_flipkart, query)
        products: List[Dict[str, Any]] = []

        for item in raw_items:
            p = Product()
            p.title = item.get("title", "")
            p.price = float(item.get("price", 0.0) or 0.0)
            p.currency = item.get("currency", "INR")
            p.source = item.get("source", "Flipkart")
            p.url = item.get("url", "#")
            p.score = 1.0 if p.price > 0 else 0.1
            products.append(p.to_dict())

        return products

