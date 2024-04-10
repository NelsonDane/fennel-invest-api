# Endpoints for Fennel API
import json


class Endpoints:
    def __init__(self):
        self.accounts = "https://accounts.fennel.com"
        self.graphql = "https://fennel-api.prod.fennel.com/graphql/"

    def retrieve_bearer_url(self):
        return f"{self.accounts}/passwordless/start"

    def oauth_url(self):
        return f"{self.accounts}/oauth/token"

    @staticmethod
    def build_graphql_payload(query, variables=None):
        if variables is None:
            variables = {}
        return {"operationName": None, "variables": variables, "query": query}

    def portfolio_query(self):
        query = """
            query GetPortfolioSummary {
                portfolio {
                    cash {
                        balance {
                            canTrade
                            canWithdraw
                            reservedBalance
                            settledBalance
                            tradeBalance
                            tradeDecrease
                            tradeIncrease
                        }
                        currency
                    }
                    totalEquityValue
                }
            }
        """
        return json.dumps(self.build_graphql_payload(query))

    def stock_holdings_query(self):
        query = """
            query MinimumPortfolioData {
                portfolio {
                    totalEquityValue
                    bulbs {
                        isin
                        investment {
                            marketValue
                            ownedShares
                        }
                        security {
                            currentStockPrice
                            ticker
                            securityName
                            securityType
                        }
                    }
                }
            }
        """
        return json.dumps(self.build_graphql_payload(query))

    def is_market_open_query(self):
        query = """
            query MarketHours {
                securityMarketInfo {
                    isOpen
                }
            }
        """
        return json.dumps(self.build_graphql_payload(query))

    def stock_search_query(self, symbol, count=5):
        # idk what count is
        query = """
            query Search($query: String!, $count: Int) {
                searchSearch {
                    searchSecurities(query: $query, count: $count) {
                        isin
                    }
                }
            }
        """
        variables = {"query": symbol, "count": count}
        return json.dumps(self.build_graphql_payload(query, variables))

    def stock_order_query(self, symbol, quantity, isin, side, priceRule):
        query = """
            mutation CreateOrder($order_details: OrderDetailsInput__!){
                orderCreateOrder(order: $order_details)
            }
        """
        variables = {
            "order_details": {
                "quantity": quantity,
                "symbol": symbol,
                "isin": isin,
                "side": side,
                "priceRule": priceRule,
                "timeInForce": "day",
                "routingOption": "exchange_ats_sdp",
            }
        }
        return json.dumps(self.build_graphql_payload(query, variables))

    @staticmethod
    def build_headers(Bearer, graphql=True):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip",
            "authorization": f"Bearer {Bearer}",
            "content-type": "application/json",
            "host": "fennel-api.prod.fennel.com",
            "user-agent": "Dart/3.3 (dart:io)",
        }
        if not graphql:
            headers["host"] = "accounts.fennel.com"
        return headers
