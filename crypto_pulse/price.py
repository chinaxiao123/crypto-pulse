"""
CoinGecko API client for CryptoPulse.
Free tier: 10-30 calls/min, no API key needed.
Features: rate limit handling, retry with backoff, in-memory caching.
"""
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import httpx

BASE_URL = "https://api.coingecko.com/api/v3"
CACHE_DIR = Path.home() / ".cache" / "crypto-pulse"
CACHE_TTL = 60  # seconds


class RateLimitError(Exception):
    """Raised when we hit CoinGecko rate limits despite retries."""


class CoinGeckoClient:
    """Thin wrapper around CoinGecko API with caching and retry."""

    def __init__(self):
        self.client = httpx.Client(timeout=15)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Cache ──────────────────────────────────────────────

    def _cache_key(self, name: str) -> Path:
        return CACHE_DIR / f"{name}.json"

    def _cache_get(self, key: str) -> Optional[dict]:
        path = self._cache_key(key)
        if not path.exists():
            return None
        age = time.time() - path.stat().st_mtime
        if age > CACHE_TTL:
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def _cache_set(self, key: str, data: dict):
        try:
            self._cache_key(key).write_text(json.dumps(data))
        except OSError:
            pass

    # ── HTTP with retry ──────────────────────────────────

    def _get(self, url: str, params: Optional[dict] = None, max_retries: int = 3) -> dict:
        """GET with automatic retry on 429 (rate limit)."""
        for attempt in range(max_retries):
            try:
                resp = self.client.get(url, params=params)
                if resp.status_code == 429:
                    wait = min(2 ** attempt * 3, 30)  # 3s, 6s, 12s...
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        raise RateLimitError(f"Rate limited after {max_retries} retries: {url}")

    # ── API Methods ──────────────────────────────────────

    def get_price(self, coin_id: str, vs_currency: str = "usd") -> Optional[dict]:
        """Fetch current price for a single coin (cached)."""
        cache_key = f"price_{coin_id}_{vs_currency}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        url = f"{BASE_URL}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        try:
            data = self._get(url, params=params)
            result = data.get(coin_id)
            if result:
                self._cache_set(cache_key, result)
            return result
        except (httpx.HTTPStatusError, RateLimitError):
            return None

    def get_coin_data(self, coin_id: str) -> Optional[dict]:
        """Fetch detailed coin data (cached)."""
        cache_key = f"coin_{coin_id}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        url = f"{BASE_URL}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false",
        }
        try:
            data = self._get(url, params=params)
            if data:
                self._cache_set(cache_key, data)
            return data
        except (httpx.HTTPStatusError, RateLimitError):
            return None

    def search_coin(self, query: str) -> Optional[list]:
        """Search for a coin by name/symbol."""
        url = f"{BASE_URL}/search"
        params = {"query": query}
        try:
            data = self._get(url, params=params)
            return data.get("coins", [])[:5]
        except (httpx.HTTPStatusError, RateLimitError):
            return None

    def get_trending(self) -> Optional[list]:
        """Get trending coins."""
        url = f"{BASE_URL}/search/trending"
        try:
            data = self._get(url)
            return data.get("coins", [])
        except (httpx.HTTPStatusError, RateLimitError):
            return None

    def get_price_batch(self, coin_ids: list[str], vs_currency: str = "usd") -> dict:
        """Fetch prices for multiple coins in one call."""
        if not coin_ids:
            return {}
        url = f"{BASE_URL}/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        try:
            return self._get(url, params=params)
        except (httpx.HTTPStatusError, RateLimitError):
            return {}

    def close(self):
        self.client.close()


# Common coin ID mappings (uppercase symbol -> CoinGecko ID)
COIN_MAP = {
    "BTC": "bitcoin",
    "BITCOIN": "bitcoin",
    "ETH": "ethereum",
    "ETHEREUM": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "POL": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "TRX": "tron",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "SUI": "sui",
    "PEPE": "pepe",
    "INJ": "injective-protocol",
    "NEAR": "near",
    "FET": "fetch-ai",
    "RNDR": "render-token",
    "MNT": "mantle",
    "STX": "blockstack",
}


def resolve_coin_id(symbol_or_name: str) -> str:
    """Resolve a symbol or name to CoinGecko coin ID."""
    s = symbol_or_name.strip().upper()
    if s in COIN_MAP:
        return COIN_MAP[s]
    return symbol_or_name.strip().lower()
