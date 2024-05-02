# Unofficial Fennel Invest API

This is an unofficial API for Fennel.com. It is a simple Python wrapper around the Fennel.com GraphQL API. It is not affiliated with Fennel.com in any way.

Fennel does everything via GraphQL, so yes, this is very slow.

This is still a work in progress, so it will have bugs and missing features. Please feel free to contribute!

## Installation

```bash
pip install fennel-invest-api
```

## Usage: Logging In

```python
from fennel_invest_api import Fennel

fennel = Fennel()
fennel.login(
    email="your-email@email.com",
    wait_for_2fa=True # When logging in for the first time, you need to wait for email 2FA
)
```

## Usage: Login to Fennel
No need to add wait for 2fa, just enter the code in the command line when requested, and it will save credentials into the directory.
```python
fennel.login(
    email="your-email@email.com",
)
```

## Usage: Get Stock Holdings
```python
positions = fennel.get_stock_holdings()
for position in positions:
    print(position)
```

## Usage: Get Portfolio
```python
portfolio = fennel.get_portfolio_summary()
print(portfolio)
```

## Usage: Placing Orders
```python
order = fennel.place_order(
    ticker="AAPL",
    quantity=1,
    side="buy", # Must be "buy" or "sell"
    price="market" # Only market orders are supported for now
)
print(order)
```

## Contributing
Found or fixed a bug? Have a feature request? Feel free to open an issue or pull request!

Enjoying the project? Feel free to Sponsor me on GitHub or Ko-fi!

[![Sponsor](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#white)](https://github.com/sponsors/NelsonDane)
[![ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white
)](https://ko-fi.com/X8X6LFCI0)

## DISCLAIMER
DISCLAIMER: I am not a financial advisor and not affiliated with Fennel.com. Use this tool at your own risk. I am not responsible for any losses or damages you may incur by using this project. This tool is provided as-is with no warranty.
