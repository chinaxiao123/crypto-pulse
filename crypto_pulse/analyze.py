"""
Market analysis module for CryptoPulse.
Optimized for batch queries to minimize API calls.
"""
from datetime import datetime
from typing import Optional
from .price import CoinGeckoClient, resolve_coin_id


def analyze_coin(symbol: str) -> Optional[dict]:
    """
    Analyze a single coin.

    Uses the shared client to avoid creating multiple connections.
    """
    client = CoinGeckoClient()
    try:
        coin_id = resolve_coin_id(symbol)

        # Get price in one call
        price_data = client.get_price(coin_id)
        if not price_data:
            results = client.search_coin(symbol)
            if results:
                coin_id = results[0]["id"]
                price_data = client.get_price(coin_id)

        if not price_data:
            return None

        # Get details in a second call
        detail = client.get_coin_data(coin_id)
        if not detail:
            return None

        return _build_result(price_data, detail, coin_id, symbol)
    finally:
        client.close()


def analyze_coins_batch(symbols: list[str]) -> dict[str, Optional[dict]]:
    """
    Analyze multiple coins in ONE batch API call (much faster).
    Returns: { "BTC": {...}, "ETH": {...}, ... }
    """
    client = CoinGeckoClient()
    try:
        # Resolve all IDs
        coin_ids = []
        id_map = {}  # coin_id -> original symbol
        for sym in symbols:
            cid = resolve_coin_id(sym)
            coin_ids.append(cid)
            id_map[cid] = sym.upper()

        # Batch price call (1 API call for all coins!)
        batch_prices = client.get_price_batch(coin_ids)

        results = {}
        for cid in coin_ids:
            sym = id_map[cid]
            price_data = batch_prices.get(cid)
            if not price_data:
                results[sym] = None
                continue

            detail = client.get_coin_data(cid)
            if detail:
                results[sym] = _build_result(price_data, detail, cid, sym)
            else:
                results[sym] = None

        return results
    finally:
        client.close()


def _build_result(price_data: dict, detail: dict, coin_id: str, symbol: str) -> dict:
    """Build a structured result dict from API responses."""
    usd = price_data.get("usd", 0)
    change_24h = price_data.get("usd_24h_change", 0)
    vol_24h = price_data.get("usd_24h_vol", 0)
    market_cap = price_data.get("usd_market_cap", 0)
    md = detail.get("market_data", {})

    result = {
        "name": detail.get("name", coin_id),
        "symbol": symbol.upper(),
        "coin_id": coin_id,
        "price_usd": usd,
        "change_24h_pct": change_24h,
        "volume_24h_usd": vol_24h,
        "market_cap_usd": market_cap,
        "rank": detail.get("market_cap_rank", "N/A"),
        "ath": md.get("ath", {}).get("usd", 0),
        "ath_change_pct": md.get("ath_change_percentage", {}).get("usd", 0),
        "low_24h": md.get("low_24h", {}).get("usd", 0),
        "high_24h": md.get("high_24h", {}).get("usd", 0),
        "circulating_supply": md.get("circulating_supply", 0),
        "total_supply": md.get("total_supply", 0),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Human-readable sentiment
    if change_24h > 5:
        result["sentiment"] = "🔥 暴涨"
    elif change_24h > 2:
        result["sentiment"] = "📈 上涨"
    elif change_24h > 0:
        result["sentiment"] = "↗️ 微涨"
    elif change_24h > -2:
        result["sentiment"] = "↘️ 微跌"
    elif change_24h > -5:
        result["sentiment"] = "📉 下跌"
    else:
        result["sentiment"] = "💥 暴跌"

    return result


def format_price(price: float) -> str:
    """Format price nicely."""
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    elif price >= 0.01:
        return f"${price:.6f}"
    else:
        return f"${price:.8f}"


def format_volume(vol: float) -> str:
    """Format volume with B/M/K suffixes."""
    if vol >= 1_000_000_000:
        return f"${vol / 1_000_000_000:.2f}B"
    elif vol >= 1_000_000:
        return f"${vol / 1_000_000:.2f}M"
    elif vol >= 1_000:
        return f"${vol / 1_000:.2f}K"
    return f"${vol:.2f}"
