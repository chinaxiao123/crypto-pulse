"""
CoinGecko API client for CryptoPulse.
Free tier: 10-30 calls/min, no API key needed.
"""
import httpx
from typing import Optional

BASE_URL = "https://api.coingecko.com/api/v3"


class CoinGeckoClient:
    """Thin wrapper around CoinGecko API."""

    def __init__(self):
        self.client = httpx.Client(timeout=15)

    def get_price(self, coin_id: str, vs_currency: str = "usd") -> Optional[dict]:
        """Fetch current price for a single coin."""
        url = f"{BASE_URL}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get(coin_id)

    def get_coin_data(self, coin_id: str) -> Optional[dict]:
        """Fetch detailed coin data (market data, description, etc.)."""
        url = f"{BASE_URL}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false",
        }
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def search_coin(self, query: str) -> Optional[list]:
        """Search for a coin by name/symbol."""
        url = f"{BASE_URL}/search"
        params = {"query": query}
        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("coins", [])[:5]

    def get_trending(self) -> Optional[list]:
        """Get trending coins."""
        url = f"{BASE_URL}/search/trending"
        resp = self.client.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("coins", [])

    def close(self):
        self.client.close()


# Common coin ID mappings
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
}


def resolve_coin_id(symbol_or_name: str) -> str:
    """Resolve a symbol or name to CoinGecko coin ID."""
    s = symbol_or_name.strip().upper()
    if s in COIN_MAP:
        return COIN_MAP[s]
    return symbol_or_name.strip().lower()
