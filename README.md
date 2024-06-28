# Unofficial Fennel Invest API

This is an unofficial API for Fennel.com. It is a simple Python wrapper around the Fennel.com GraphQL API. It is not affiliated with Fennel.com in any way.

Fennel does everything via GraphQL, so yes, this is very slow.

This is still a work in progress, so it will have bugs and missing features. Please feel free to contribute!

## Important!
Do not use any version of this library before 1.0.9. Earlier versions had a bug with placing certain orders that when executed excessively could lead to your account being locked. This has been fixed in 1.0.9. See [this issue](https://github.com/NelsonDane/fennel-invest-api/issues/14)

## Installation

```bash
pip install 'fennel-invest-api>=1.0.9'
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

If you'd like to handle the 2FA yourself programmatically instead of waiting for `input()`, you can call it with `wait_for_2fa=False`, catch the 2FA exception, then call it again with the 2FA code:

```python
fennel.login(
    email="your-email@email.com",
    wait_for_2fa=False
    code="123456" # Should be six-digit integer from email
)
```

## Usage: Get Stock Holdings
```python
account_ids = fennel.get_account_ids()
for account_id in account_ids:
    print(account_id)
    positions = fennel.get_stock_holdings(account_id)
    for position in positions:
        print(position)
```

## Usage: Get Portfolio
```python
# For all accounts
full_portfolio = fennel.get_full_accounts() # This endpoint may return 503. If it does, then run fennel.get_account_ids() and loop through the accounts
print(full_portfolio)
# For a single account ID
portfolio = fennel.get_portfolio_summary(account_id)
print(portfolio)
```

## Usage: Placing Orders
```python
order = fennel.place_order(
    account_id=account_id,
    symbol="AAPL",
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