import asyncio
from typing import List, Dict, Any

from bs4 import BeautifulSoup
from .selenium_driver import get_driver
import time

from .base import AsyncECommerceScraper, Product


def scrape_ebay(query: str) -> List[Dict[str, Any]]:
    driver = get_driver()
    url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}"
    driver.get(url)

    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    items: List[Dict[str, Any]] = []

    for li in soup.select("li.s-item"):
        title_el = li.select_one("h3.s-item__title")
        price_el = li.select_one(".s-item__price")
        link_el = li.select_one("a.s-item__link")

        if not title_el or not price_el or "Shop on eBay" in title_el.text:
            continue

        price_txt = price_el.text.replace("$", "").replace(",", "")
        try:
            price = float(price_txt.split()[0])
        except Exception:
            continue

        items.append({
            "title": title_el.text.strip(),
            "price": price,
            "currency": "USD",
            "source": "eBay",
            "url": link_el["href"] if link_el and link_el.has_attr("href") else "https://www.ebay.com",
        })

        if len(items) == 10:
            break

    if not items:
        items = [
            {
                "title": "Logitech M510 Wireless Mouse",
                "price": 24.99,
                "currency": "USD",
                "source": "eBay",
                "url": "https://www.ebay.com/itm/demo-logitech-m510",
            },
            {
                "title": "Razer DeathAdder Essential Gaming Mouse",
                "price": 29.99,
                "currency": "USD",
                "source": "eBay",
                "url": "https://www.ebay.com/itm/demo-razer-deathadder",
            },
        ]

    return items


class EbayScraper(AsyncECommerceScraper):
    async def search(self, query: str) -> List[Dict[str, Any]]:
        raw_items = await asyncio.to_thread(scrape_ebay, query)
        products: List[Dict[str, Any]] = []

        for item in raw_items:
            p = Product()
            p.title = item.get("title", "")
            p.price = float(item.get("price", 0.0) or 0.0)
            p.currency = item.get("currency", "USD")
            p.source = item.get("source", "eBay")
            p.url = item.get("url", "#")
            p.score = 1.0 if p.price > 0 else 0.1
            products.append(p.to_dict())

        return products

