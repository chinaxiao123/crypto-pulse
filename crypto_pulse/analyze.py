"""
Market analysis module for CryptoPulse.
"""
from datetime import datetime
from typing import Optional, Tuple
from .price import CoinGeckoClient, resolve_coin_id


def analyze_coin(symbol: str) -> Optional[dict]:
    """
    Analyze a coin and return structured data.
    Returns None if coin not found.
    """
    client = CoinGeckoClient()
    coin_id = resolve_coin_id(symbol)

    price_data = client.get_price(coin_id)
    if not price_data:
        # Try searching
        results = client.search_coin(symbol)
        if results:
            coin_id = results[0]["id"]
            price_data = client.get_price(coin_id)

    if not price_data:
        client.close()
        return None

    # Get detailed data
    detail = client.get_coin_data(coin_id)
    client.close()

    if not detail:
        return None

    usd = price_data.get("usd", 0)
    change_24h = price_data.get("usd_24h_change", 0)
    vol_24h = price_data.get("usd_24h_vol", 0)
    market_cap = price_data.get("usd_market_cap", 0)

    result = {
        "name": detail.get("name", coin_id),
        "symbol": detail.get("symbol", symbol).upper(),
        "coin_id": coin_id,
        "price_usd": usd,
        "change_24h_pct": change_24h,
        "volume_24h_usd": vol_24h,
        "market_cap_usd": market_cap,
        "rank": detail.get("market_cap_rank", "N/A"),
        "ath": detail.get("market_data", {}).get("ath", {}).get("usd", 0),
        "ath_change_pct": detail.get("market_data", {}).get("ath_change_percentage", {}).get("usd", 0),
        "low_24h": detail.get("market_data", {}).get("low_24h", {}).get("usd", 0),
        "high_24h": detail.get("market_data", {}).get("high_24h", {}).get("usd", 0),
        "circulating_supply": detail.get("market_data", {}).get("circulating_supply", 0),
        "total_supply": detail.get("market_data", {}).get("total_supply", 0),
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
    """Format volume with B/M suffixes."""
    if vol >= 1_000_000_000:
        return f"${vol/1_000_000_000:.2f}B"
    elif vol >= 1_000_000:
        return f"${vol/1_000_000:.2f}M"
    elif vol >= 1_000:
        return f"${vol/1_000:.2f}K"
    else:
        return f"${vol:.2f}"
