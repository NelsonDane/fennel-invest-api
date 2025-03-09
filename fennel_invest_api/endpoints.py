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
                        ... on Account {
                            name
                            id
                            created
                            isPrimary
                            status
                        }
                        ... on RothIRA {
                            name
                            id
                            created
                            isPrimary
                            status
                        }
                        ... on TraditionalIRA {
                            name
                            id
                            created
                            isPrimary
                            status
                        }
                    }
                }
            }
        """
        return json.dumps(self.build_graphql_payload(query))

    def portfolio_query(self, account_id):
        query = """
            query GetPortfolioSummary($accountId: String!) {
                account(accountId: $accountId) {
                    ... on Account {
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
                    ... on RothIRA {
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
                    ... on TraditionalIRA {
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
            }
        """
        return json.dumps(self.build_graphql_payload(query, {"accountId": account_id}))

    def stock_holdings_query(self, account_id):
        query = """
            query MinimumPortfolioData($accountId: String!) {
                account(accountId: $accountId) {
                    ... on Account {
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
                    ... on RothIRA {
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
                    ... on TraditionalIRA {
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

    def is_tradable_query(self, isin, account_id):
        query = """
            query GetTradeable($isin: String!, $accountId: String) {
                bulbBulb(isin: $isin) {
                    tradeable(accountId: $accountId) {
                        canBuy
                        canSell
                        restrictionReason
                    }
                }
            }
        """
        variables = {"isin": isin, "accountId": account_id}
        return json.dumps(self.build_graphql_payload(query, variables))

    def stock_search_query(self, symbol, count=5):
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
            "user-agent": "Fennel/1.6.48+6276 (Generic Android-x86_64; Android 13) Dart/3.5.3 (dart:io)",
        }
        if Bearer is not None:
            headers["authorization"] = f"Bearer {Bearer}"
        if accounts_host:
            headers["host"] = "accounts.fennel.com"
        return headers
