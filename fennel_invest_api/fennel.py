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
        self.account_number = (
            "00000000"  # Fennel only has 1 account which they don't share
        )
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
        # If creds exist, then see if they are valid
        if self.Bearer is not None:
            if self._verify_login():
                return True
            self._clear_credentials()
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
        self._save_credentials()
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
        self.Bearer = f"{response['access_token']}"
        self.Refresh = response["refresh_token"]
        self.ID_Token = response["id_token"]
        return response

    def _verify_login(self):
        # Test login by getting portfolio summary
        try:
            self.get_portfolio_summary()
            return True
        except Exception:
            try:
                self.refresh_token()
                self.get_portfolio_summary()
                return True
            except Exception:
                return False

    @check_login
    def get_portfolio_summary(self):
        query = self.endpoints.portfolio_query()
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Portfolio Request failed with status code {response.status_code}: {response.text}"
            )
        return response.json()["data"]["portfolio"]

    @check_login
    def get_stock_holdings(self):
        query = self.endpoints.stock_holdings_query()
        headers = self.endpoints.build_headers(self.Bearer)
        response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if response.status_code != 200:
            raise Exception(
                f"Stock Holdings Request failed with status code {response.status_code}: {response.text}"
            )
        response = response.json()
        return response["data"]["portfolio"]["bulbs"]

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
    def place_order(self, ticker, quantity, side, price="market", dry_run=False):
        if side.lower() not in ["buy", "sell"]:
            raise Exception("Side must be either 'buy' or 'sell'")
        # Check if market is open
        if not self.is_market_open():
            raise Exception("Market is closed. Cannot place order.")
        # Search for stock "isin"
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
        if dry_run:
            return search_response
        if len(search_response["data"]["searchSearch"]["searchSecurities"]) == 0:
            raise Exception(f"No stock found with ticker {ticker}. Please check the app to see if it is valid.")
        isin = search_response["data"]["searchSearch"]["searchSecurities"][0]["isin"]
        # Place order
        query = self.endpoints.stock_order_query(ticker, quantity, isin, side, price)
        order_response = self.session.post(
            self.endpoints.graphql, headers=headers, data=query
        )
        if order_response.status_code != 200:
            raise Exception(
                f"Order Request failed with status code {order_response.status_code}: {order_response.text}"
            )
        return order_response.json()
