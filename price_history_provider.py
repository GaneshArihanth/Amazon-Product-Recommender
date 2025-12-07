from typing import Optional


class PriceHistoryProvider:
    """Optional external price history provider.

    This is a stub that can be extended to call services like pricehistory.app
    for supported Amazon URLs. If no external data is available, it should
    return None so the local PriceTracker logic is used instead.
    """

    def get_advice(self, url: str) -> Optional[str]:
        """Return a human-readable advice string, or None if not available."""
        # Stub: always fall back to local tracker for now.
        return None
