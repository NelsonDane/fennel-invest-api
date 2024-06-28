import os
import pickle

import requests

from fennel_invest_api.endpoints import Endpoints


def check_login(func):
    def wrapper(self, *args, **kwargs):
        if self.Bearer is None:
            raise Exception("Bearer token is not set. Please login first.")
        return func(self, *args, **kwargs)

    return wrapper


class Fennel:
    def __init__(self, filename="fennel_credentials.pkl", path=None) -> None:
        self.session = requests.Session()
        self.endpoints = Endpoints()
        self.Bearer = None
        self.Refresh = None
        self.ID_Token = None
        self.timeout = 10
        self.account_ids = []  # For multiple accounts
        self.client_id = "FXGlhcVdamwozAFp8BZ2MWl6coPl6agX"
        self.filename = filename
        self.path = None
        if path is not None:
            self.path = path
        self._load_credentials()

    def _load_credentials(self):
        filename = self.filename
        if self.path is not None:
            filename = os.path.join(self.path, filename)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                credentials = pickle.load(f)
            self.Bearer = credentials.get("Bearer")
            self.Refresh = credentials.get("Refresh")
            self.ID_Token = credentials.get("ID_Token")
            self.client_id = credentials.get("client_id", self.client_id)

    def _save_credentials(self):
        filename = self.filename
        if self.path is not None:
            filename = os.path.join(self.path, filename)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        with open(filename, "wb") as f:
            pickle.dump(
                {
                    "Bearer": self.Bearer,
                    "Refresh": self.Refresh,
                    "ID_Token": self.ID_Token,
                    "client_id": self.client_id,
                },
                f,
            )

    def _clear_credentials(self):
        filename = self.filename
        if self.path is not None:
            filename = os.path.join(self.path, filename)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        if os.path.exists(filename):
            os.remove(filename)
        self.Bearer = None
        self.Refresh = None
        self.ID_Token = None

    def login(self, email, wait_for_code=True, code=None):
        # If creds exist, check if they are valid/try to refresh
        if self.Bearer is not None and self._verify_login():
            return True
        if code is None:
            url = self.endpoints.retrieve_bearer_url()
            payload = {
                "email": email,
                "client_id": self.client_id,
                "connection": "email",
                "send": "code",
            }
            response = self.session.post(url, json=payload)
            if response.status_code != 200:
                raise Exception(f"Failed to start passwordless login: {response.text}")
            if not wait_for_code:
                raise Exception("2FA required. Please provide the code.")
            print("2FA code sent to email")
            code = input("Enter 2FA code: ")
        url = self.endpoints.oauth_url()
        payload = {
            "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
            "client_id": self.client_id,
            "otp": str(code),
            "username": email,
            "scope": "openid profile offline_access email",
            "audience": "https://meta.api.fennel.com/graphql",
            "realm": "email",
        }
        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to login: {response.text}")
        response = response.json()
        self.Bearer = response["access_token"]
        self.Refresh = response["refresh_token"]
        self.ID_Token = response["id_token"]
        self.refresh_token()
        self.get_account_ids()
        return True

    def refresh_token(self):
        url = self.endpoints.oauth_url()
        headers = self.endpoints.build_headers(accounts_host=True)
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.Refresh,
            "scope": "openid profile offline_access email",
        }
        response = self.session.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to refresh bearer token: {response.text}")
        response = response.json()
        self.Bearer = response["access_token"]
        self.Refresh = response["refresh_token"]
        self.ID_Token = response["id_token"]
        self._save_credentials()
        return response

    def _verify_login(self):
        # Test login by getting Account IDs
        try:
            self.get_account_ids()
            return True
        except Exception:
            try:
                # Try to refresh token
                self.refresh_token()
                self.get_account_ids()
                return True
            except Exception as e:
                # Unable to refresh, clear credentials
                print(f"Failed to refresh token: {e}")
                self._clear_credentials()
                return False

    @check_login
    def get_account_ids(self):
        query = self.endpoints.account_ids_query()
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Account ID Check failed with status code {response.status_code}: {response.text}"
            )
        response = response.json()["data"]["user"]["accounts"]
        response_list = sorted(response, key=lambda x: x["created"])
        account_ids = []
        for account in response_list:
            if account["status"] == "APPROVED":
                account_ids.append(account["id"])
        self.account_ids = account_ids
        return account_ids

    @check_login
    def get_full_accounts(self):
        # query = self.endpoints.list_full_accounts_query()
        query = self.endpoints.account_ids_query()
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Full Account Request failed with status code {response.status_code}: {response.text}"
            )
        response = response.json()["data"]["user"]["accounts"]
        response_list = sorted(response, key=lambda x: x["created"])
        approved_accounts = []
        for account in response_list:
            if account["status"] == "APPROVED":
                approved_accounts.append(account)
        return approved_accounts

    @check_login
    def get_portfolio_summary(self, account_id):
        query = self.endpoints.portfolio_query(account_id)
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Portfolio Request failed with status code {response.status_code}: {response.text}"
            )
        return response.json()["data"]["account"]["portfolio"]

    @check_login
    def get_stock_quote(self, ticker):
        query = self.endpoints.stock_search_query(ticker)
        headers = self.endpoints.build_headers(self.Bearer)
        search_response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if search_response.status_code != 200:
            raise Exception(
                f"Stock Search Request failed with status code {search_response.status_code}: {search_response.text}"
            )
        search_response = search_response.json()
        securities = search_response["data"]["searchSearch"]["searchSecurities"]
        if len(securities) == 0:
            raise Exception(
                f"No stock found with ticker {ticker}. Please check the app to see if it is valid."
            )
        stock_quote = next(
            (
                x
                for x in securities
                if x["security"]["ticker"].lower() == ticker.lower()
            ),
            None,
        )
        return stock_quote

    @check_login
    def get_stock_price(self, ticker):
        quote = self.get_stock_quote(ticker)
        return None if quote is None else quote["security"]["currentStockPrice"]

    @check_login
    def get_stock_holdings(self, account_id):
        query = self.endpoints.stock_holdings_query(account_id)
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Stock Holdings Request failed with status code {response.status_code}: {response.text}"
            )
        response = response.json()
        return response["data"]["account"]["portfolio"]["bulbs"]

    @check_login
    def is_market_open(self):
        query = self.endpoints.is_market_open_query()
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Market Open Request failed with status code {response.status_code}: {response.text}"
            )
        response = response.json()
        return response["data"]["securityMarketInfo"]["isOpen"]

    @check_login
    def get_stock_isin(self, ticker):
        quote = self.get_stock_quote(ticker)
        return None if quote is None else quote["isin"]

    @check_login
    def place_order(
        self, account_id, ticker, quantity, side, price="market", dry_run=False
    ):
        if side.lower() not in ["buy", "sell"]:
            raise Exception("Side must be either 'buy' or 'sell'")
        # Check if market is open
        if not self.is_market_open():
            raise Exception("Market is closed. Cannot place order.")
        # Search for stock "isin"
        isin = self.get_stock_isin(ticker)
        if isin is None:
            raise Exception(f"Failed to find ISIN for stock with ticker {ticker}")
        if dry_run:
            return {
                "account_id": account_id,
                "ticker": ticker,
                "quantity": quantity,
                "isin": isin,
                "side": side,
                "price": price,
                "dry_run_success": True,
            }
        # Place order
        query = self.endpoints.stock_order_query(
            account_id, ticker, quantity, isin, side, price
        )
        headers = self.endpoints.build_headers(self.Bearer)
        order_response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if order_response.status_code != 200:
            raise Exception(
                f"Order Request failed with status code {order_response.status_code}: {order_response.text}"
            )
        return order_response.json()
