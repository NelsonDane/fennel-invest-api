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

    def account_ids_query(self):
        query = """
            query Check {
                user {
                    id
                    accounts {
                        name
                        id
                        created
                        isPrimary
                        status
                    }
                }
            }
        """
        return json.dumps(self.build_graphql_payload(query))

    # This returns 503 for some users,
    # so best to run account_ids_query and then portfolio_query
    # def list_full_accounts_query(self):
    #     query = """
    #         query ListFullAccounts {
    #             user {
    #                 id
    #                 accounts {
    #                     name
    #                     id
    #                     created
    #                     isPrimary
    #                     status
    #                     portfolio {
    #                         id
    #                         totalEquityValue
    #                         cash {
    #                             balance {
    #                                 canTrade
    #                                 canWithdraw
    #                                 reservedBalance
    #                                 settledBalance
    #                                 tradeBalance
    #                                 tradeDecrease
    #                                 tradeIncrease
    #                             }
    #                             currency
    #                         }
    #                         totalEquityValue
    #                     }
    #                 }
    #             }
    #         }
    #     """
    #     return json.dumps(self.build_graphql_payload(query))

    def portfolio_query(self, account_id):
        query = """
            query GetPortfolioSummary($accountId: String!) {
                account(accountId: $accountId) {
                    id
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
            }
        """
        return json.dumps(self.build_graphql_payload(query, {"accountId": account_id}))

    def stock_holdings_query(self, account_id):
        query = """
            query MinimumPortfolioData($accountId: String!) {
                account(accountId: $accountId) {
                    id
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
            }
        """
        return json.dumps(self.build_graphql_payload(query, {"accountId": account_id}))

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
                        security {
                            currentStockPrice
                            ticker
                        }
                    }
                }
            }
        """
        variables = {"query": symbol, "count": count}
        return json.dumps(self.build_graphql_payload(query, variables))

    def stock_order_query(self, account_id, symbol, quantity, isin, side, priceRule):
        query = """
            mutation CreateOrder(
                $order_details: OrderDetailsInput__!
                $accountId: String!
            ) {
                createOrder(
                    accountId: $accountId
                    order: $order_details
                )
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
            },
            "accountId": account_id,
        }
        return json.dumps(self.build_graphql_payload(query, variables))

    @staticmethod
    def build_headers(Bearer=None, accounts_host=False):
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip",
            "content-type": "application/json",
            "host": "fennel-api.prod.fennel.com",
            "user-agent": "Dart/3.3 (dart:io)",
        }
        if Bearer is not None:
            headers["authorization"] = f"Bearer {Bearer}"
        if accounts_host:
            headers["host"] = "accounts.fennel.com"
        return headers
