"""
Report generation for CryptoPulse.
Generates Markdown reports suitable for Binance Square posting.
Uses batch API for efficiency.
"""
from datetime import datetime
from typing import Optional
from .analyze import analyze_coins_batch, format_price, format_volume


def generate_daily_report(
    coins: list[str], persona: str = "default"
) -> Optional[str]:
    """
    Generate a daily market report in Markdown (uses batch API).

    Args:
        coins: List of coin symbols (e.g. ['BTC', 'ETH', 'BNB'])
        persona: 'default' or '八手玫瑰' for different writing styles

    Returns:
        Markdown string, or None if all coins failed
    """
    # Single batch API call for all coins
    data = analyze_coins_batch(coins)

    # Filter out failed lookups
    data = {k: v for k, v in data.items() if v is not None}

    if not data:
        return None

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if persona == "八手玫瑰":
        return _generate_rose_report(data, timestamp)
    else:
        return _generate_default_report(data, timestamp)


def _generate_default_report(data: dict, timestamp: str) -> str:
    """Standard report format."""
    lines = [f"# 📊 Crypto Market Report", f"*Generated: {timestamp}*", ""]

    # Overview table
    lines.append("## Market Overview")
    lines.append("")
    lines.append("| Coin | Price | 24h Change | Volume 24h | Market Cap | Sentiment |")
    lines.append("|------|-------|-----------|------------|------------|-----------|")

    total_change = 0.0
    for symbol, info in data.items():
        change = info.get("change_24h_pct", 0) or 0
        total_change += change
        change_str = f"{change:+.2f}%"
        lines.append(
            f"| {symbol} | {format_price(info['price_usd'])} | {change_str} | "
            f"{format_volume(info['volume_24h_usd'])} |"
            f" {format_volume(info['market_cap_usd'])} |"
            f" {info.get('sentiment', 'N/A')} |"
        )

    lines.append("")
    avg_change = total_change / len(data) if data else 0
    lines.append(f"**Average 24h Change:** {avg_change:+.2f}%")
    lines.append("")

    # Per-coin details
    lines.append("## Details")
    lines.append("")
    for symbol, info in data.items():
        lines.append(f"### {symbol} ({info['name']})")
        lines.append(f"- **Price:** {format_price(info['price_usd'])}")
        lines.append(f"- **24h Change:** {info['change_24h_pct']:+.2f}%")
        lines.append(f"- **24h High:** {format_price(info['high_24h'])}")
        lines.append(f"- **24h Low:** {format_price(info['low_24h'])}")
        lines.append(f"- **Volume:** {format_volume(info['volume_24h_usd'])}")
        lines.append(f"- **Market Cap:** {format_volume(info['market_cap_usd'])}")
        lines.append(f"- **Market Rank:** #{info['rank']}")
        lines.append(f"- **Sentiment:** {info['sentiment']}")
        lines.append("")

    lines.append("---")
    lines.append("*Powered by [CryptoPulse](https://github.com/chinaxiao123/crypto-pulse) 💓*")
    return "\n".join(lines)


def _generate_rose_report(data: dict, timestamp: str) -> str:
    """
    🎭 八手玫瑰风格报告 — 幽默反讽、数据驱动、短平快
    """
    lines = [
        "兄弟们，重仓猛干！🌹",
        "",
        f"> {timestamp} 行情速报，情报员八手玫瑰为您播报",
        "",
    ]

    for symbol, info in data.items():
        change = info.get("change_24h_pct", 0) or 0
        sentiment = info.get("sentiment", "")
        price = format_price(info["price_usd"])

        if change > 5:
            emoji = "🚀🚀🚀"
            comment = "起飞了兄弟们，再不上车就来不及了！"
        elif change > 2:
            emoji = "📈"
            comment = "稳步上涨，多军狂欢中"
        elif change > 0:
            emoji = "↗️"
            comment = "小涨怡情，格局打开"
        elif change > -2:
            emoji = "↘️"
            comment = "回调就是机会，你细品"
        elif change > -5:
            emoji = "📉"
            comment = "跌了别慌，富贵险中求"
        else:
            emoji = "💥"
            comment = "血洗！但重仓猛干的人从不撤退"

        lines.append(f"### {symbol} {emoji}")
        lines.append(f"**现价:** {price}")
        lines.append(f"**24h:** {change:+.2f}% ({sentiment})")
        lines.append(f"**成交量:** {format_volume(info['volume_24h_usd'])}")
        lines.append(f"> {comment}")
        lines.append("")

    lines.append("---")
    lines.append("*本内容仅为情报分享，不构成投资建议 DYOR* 🔍")
    lines.append("*Powered by [CryptoPulse](https://github.com/chinaxiao123/crypto-pulse) 💓 + 八手玫瑰 🌹*")
    return "\n".join(lines)
