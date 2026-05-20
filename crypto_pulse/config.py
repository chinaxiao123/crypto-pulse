"""
Configuration module for CryptoPulse.
"""
import os
from pathlib import Path

# Config file location
CONFIG_DIR = Path.home() / ".config" / "crypto-pulse"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

# Default config
DEFAULT_CONFIG = {
    "default_currency": "usd",
    "default_coins": ["BTC", "ETH", "BNB", "SOL"],
    "persona": "default",
    "binance_square": {
        "api_key": "",
        "enabled": False,
    },
}


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_config() -> dict:
    """Load config from file or return defaults."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        import yaml
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **yaml.safe_load(f)}
    return dict(DEFAULT_CONFIG)


def save_config(config: dict):
    """Save config to file."""
    ensure_config_dir()
    import yaml
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
