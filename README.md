# CryptoPulse

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CoinGecko](https://img.shields.io/badge/API-CoinGecko-orange)](https://www.coingecko.com)

> **加密市场行情分析CLI工具** — 实时行情、数据分析、一键报告

## Features

```bash
🚀 crypto pulse BTC         → 比特币实时行情
📊 crypto analyze ETH        → 以太坊深度分析
📝 crypto report             → 生成 Markdown 日报
🎭 crypto post               → 币安广场自动发帖（八手玫瑰🌹）
```

## Quick Start

```bash
pip install -r requirements.txt

# 查 BTC 价格
python -m crypto_pulse.cli pulse BTC

# 分析 ETH
python -m crypto_pulse.cli analyze ETH

# 日报
python -m crypto_pulse.cli report
```

## Tech Stack

- **Python** + **Typer** — CLI framework
- **CoinGecko API** — Free crypto data
- **Rich** — Beautiful terminal output
- **Markdown** — Report generation

## Roadmap

- [x] Real-time price query
- [ ] K-line chart
- [ ] Multi-coin comparison
- [ ] AI analysis (DeepSeek/Claude)
- [ ] Binance Square auto-posting
- [ ] Scheduled daily reports

---

**⭐ Star if you find this useful!**
