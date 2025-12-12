# scrapers/base.py
import aiohttp
import asyncio
import random
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

FULL_HEADERS = [
    {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1",
    }
    for ua in [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    ]
]


class BaseScraper:
    async def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """Low-level HTML fetch helper with retries.

        Returns a BeautifulSoup instance on success, otherwise None.
        """
        headers = random.choice(FULL_HEADERS).copy()
        # Add a referer to look more like a browser flow
        headers.setdefault("Referer", "https://www.google.com/")

        # Configurable jitter and concurrency
        try:
            delay_min = float(os.getenv("SCRAPER_DELAY_MIN", "0.8"))
            delay_max = float(os.getenv("SCRAPER_DELAY_MAX", "2.0"))
            limit_per_host = int(os.getenv("SCRAPER_LIMIT_PER_HOST", "2"))
        except Exception:
            delay_min, delay_max, limit_per_host = 0.8, 2.0, 2

        proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")

        for attempt in range(3):
            try:
                # Jitter between attempts to reduce 503s
                await asyncio.sleep(random.uniform(delay_min, delay_max))

                timeout = aiohttp.ClientTimeout(total=15)
                connector = aiohttp.TCPConnector(limit_per_host=limit_per_host)
                async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                    async with session.get(url, headers=headers, proxy=proxy) as resp:

                        if resp.status == 200:
                            text = await resp.text()
                            return BeautifulSoup(text, "html.parser")

                        logger.warning(f"Status {resp.status} for {url}")
                        # Backoff more on 429/503
                        if resp.status in (429, 503):
                            await asyncio.sleep((attempt + 1) * 2 + random.uniform(0, 1))

            except Exception as e:
                logger.error(f"Fetch error attempt {attempt+1}: {e}")

            await asyncio.sleep(1)

        return None


@dataclass
class Product:
    """Simple container used by async scrapers.

    This mirrors the structure expected by the agent: a dict with
    title, price, currency, source, url and score fields.
    """

    title: str = ""
    price: float = 0.0
    currency: str = "USD"
    source: str = ""
    url: str = "#"
    image_url: str = ""
    score: float = 1.0
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "source": self.source,
            "url": self.url,
            "image_url": self.image_url,
            "score": self.score,
        }
        data.update(self.extra)
        return data


class AsyncECommerceScraper(BaseScraper):
    """Base class for site-specific async scrapers.

    Child classes should implement ``async def search(self, query: str)``
    and return ``List[Dict[str, Any]]`` where each dict matches
    the structure produced by ``Product.to_dict``.
    """

    async def search(self, query: str) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError

