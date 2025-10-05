# Unofficial Fennel Invest API

This is an unofficial API for Fennel.com (now) built using the official [Fennel API](https://api.fennel.com/docs#tag/Welcome). This project is not affiliated with Fennel.com in any way.

While I try my best to ensure the API is working correctly, it is an ongoing work in progress, so it may have bugs and missing features. Please feel free to contribute!

## Important!
Versions prior to `2.0.0` used an unofficial reverse-engineered API that mimicked the Fennel Invest mobile app. With the release of the official API, this library has been updated to use that instead and previous versions are no longer supported or recommended.

## Installation
Install with [uv](https://github.com/astral-sh/uv):

```bash
uv add 'fennel-invest-api>=2.0.0'
```

Or with pip:
```bash
pip install 'fennel-invest-api>=2.0.0'
```

## Usage: Logging In
Generate a new Personal Access Token (PAT) from the [Fennel Dashboard](https://dash.fennel.com/).

Then, initialize the `Fennel` class with your `PAT`:
```python
from fennel_invest_api import Fennel

fennel = Fennel(pat_token="your-personal-access-token")
```

## Usage: Get Account Info
```python
account_info = fennel.get_account_info()
for account in account_info:
    print(f"Name: {account.name}, Account ID: {account.id}, Type: {account.account_type}")
```

## Usage: Get Account Summary
```python
account_info = fennel.get_account_info()
for account in account_info:
    summary = fennel.get_portfolio_cash_summary(account.id)
    print(f"Account: {account.name}, Portfolio Value: ${summary.portfolio_value:.2f}, Buying Power: ${summary.buying_power:.2f}, Cash: ${summary.cash_available:.2f}")
```

## Usage: Get Stock Holdings
```python
account_info = fennel.get_account_info()
for account_id in account_info:
    positions = fennel.get_portfolio_positions(account_id.id)
    print(f"Positions for account {account_id.name}:")
    for position in positions:
        print(f"{position.symbol}: {position.shares} shares at ${position.value:.2f}")
```

## Usage: Placing Orders
Market order (Default):
```python
order = fennel.place_order(
    account_id=account_id,
    symbol="AAPL",
    shares=1,
    side="BUY"
)
print(order)
```

Limit order:
```python
order = fennel.place_order(
    account_id=account_id,
    ticker="AAPL",
    quantity=1,
    side="BUY",
    order_type="LIMIT",
    limit_price=150.00,
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
