"""
CryptoPulse CLI - Main entry point.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .price import CoinGeckoClient, resolve_coin_id
from .analyze import analyze_coin, format_price, format_volume
from .report import generate_daily_report
from .config import get_config

app = typer.Typer(
    name="crypto-pulse",
    help="💓 CryptoPulse - 加密市场行情分析CLI工具",
    add_completion=False,
)
console = Console()


@app.callback()
def callback():
    """💓 CryptoPulse — Real-time crypto market data CLI tool"""
    pass


@app.command()
def pulse(
    coin: str = typer.Argument("BTC", help="Coin symbol or name (e.g. BTC, ETH, SOL)"),
    currency: str = typer.Option("usd", "--currency", "-c", help="Currency"),
):
    """🚀 Get real-time price for a coin"""
    client = CoinGeckoClient()
    coin_id = resolve_coin_id(coin)

    price_data = client.get_price(coin_id, currency)
    if not price_data:
        console.print(f"[red]❌ Coin '{coin}' not found. Try searching with: crypto search {coin}[/red]")
        client.close()
        raise typer.Exit(1)

    usd_price = price_data.get(currency, 0)
    change = price_data.get(f"{currency}_24h_change", 0)
    vol = price_data.get(f"{currency}_24h_vol", 0)
    mcap = price_data.get(f"{currency}_market_cap", 0)

    change_str = f"{change:+.2f}%" if change else "N/A"
    price_str = format_price(usd_price)

    table = Table(box=box.ROUNDED, title=f"💓 {coin.upper()} Pulse")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Price", price_str)
    table.add_row("24h Change", change_str)
    table.add_row("24h Volume", format_volume(vol))
    table.add_row("Market Cap", format_volume(mcap))

    console.print(table)
    client.close()


@app.command()
def analyze(
    coin: str = typer.Argument("BTC", help="Coin symbol or name"),
):
    """📊 Deep analysis of a coin"""
    with console.status(f"[bold green]Analyzing {coin}..."):
        result = analyze_coin(coin)

    if not result:
        console.print(f"[red]❌ Could not analyze '{coin}'[/red]")
        raise typer.Exit(1)

    # Main info
    table = Table(box=box.ROUNDED, title=f"📊 {result['name']} ({result['symbol']}) Analysis")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Price", format_price(result['price_usd']))
    table.add_row("24h Change", f"{result['change_24h_pct']:+.2f}%")
    table.add_row("24h High", format_price(result['high_24h']))
    table.add_row("24h Low", format_price(result['low_24h']))
    table.add_row("Volume (24h)", format_volume(result['volume_24h_usd']))
    table.add_row("Market Cap", format_volume(result['market_cap_usd']))
    table.add_row("Market Rank", f"#{result['rank']}")
    table.add_row("ATH", format_price(result['ath']))
    table.add_row("Sentiment", result['sentiment'])

    console.print(table)


@app.command()
def report(
    coins: str = typer.Option("BTC,ETH,BNB,SOL", "--coins", "-c", help="Comma-separated coin list"),
    persona: str = typer.Option("default", "--persona", "-p", help="Report style: default or 八手玫瑰"),
    output: str = typer.Option("", "--output", "-o", help="Output file path"),
):
    """📝 Generate market report"""
    coin_list = [c.strip() for c in coins.split(",")]

    with console.status(f"[bold green]Generating {persona} report for {coin_list}..."):
        result = generate_daily_report(coin_list, persona)

    if not result:
        console.print("[red]❌ Failed to generate report[/red]")
        raise typer.Exit(1)

    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[green]✅ Report saved to {output}[/green]")
    else:
        console.print(Panel(result, title="📝 Market Report", border_style="green"))


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
):
    """🔍 Search for a coin"""
    client = CoinGeckoClient()
    results = client.search_coin(query)
    client.close()

    if not results:
        console.print(f"[yellow]No results for '{query}'[/yellow]")
        return

    table = Table(box=box.ROUNDED, title=f"🔍 Search: {query}")
    table.add_column("Coin", style="cyan")
    table.add_column("Symbol", style="yellow")
    table.add_column("ID", style="green")
    table.add_column("Market Cap Rank", style="blue")

    for coin in results:
        table.add_row(
            coin.get("name", "?"),
            coin.get("symbol", "?").upper(),
            coin.get("id", "?"),
            str(coin.get("market_cap_rank", "N/A")),
        )

    console.print(table)


@app.command()
def trending():
    """🔥 Show trending coins"""
    client = CoinGeckoClient()
    coins = client.get_trending()
    client.close()

    if not coins:
        console.print("[yellow]No trending data available[/yellow]")
        return

    table = Table(box=box.ROUNDED, title="🔥 Trending Coins")
    table.add_column("#", style="dim")
    table.add_column("Coin", style="cyan")
    table.add_column("Symbol", style="yellow")
    table.add_column("Price", style="green")

    for i, item in enumerate(coins[:10], 1):
        coin = item.get("item", {})
        price = coin.get("data", {}).get("price", "N/A")
        if isinstance(price, (int, float)):
            price = format_price(price)
        table.add_row(
            str(i),
            coin.get("name", "?"),
            coin.get("symbol", "?").upper(),
            str(price),
        )

    console.print(table)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current config"),
    set_default_coins: str = typer.Option("", "--set-coins", help="Set default coins (comma-separated)"),
    set_persona: str = typer.Option("", "--set-persona", help="Set default persona (default/八手玫瑰)"),
):
    """⚙️ Manage configuration"""
    cfg = get_config()

    if show:
        import yaml
        console.print(Panel(yaml.dump(cfg, default_flow_style=False), title="⚙️ Config"))
        return

    if set_default_coins:
        cfg["default_coins"] = [c.strip() for c in set_default_coins.split(",")]

    if set_persona:
        cfg["persona"] = set_persona

    from .config import save_config
    save_config(cfg)
    console.print("[green]✅ Config updated[/green]")


def main():
    """Entry point for CLI."""
    app()
