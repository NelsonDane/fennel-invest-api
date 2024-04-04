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

    def build_graphql_payload(self, query):
        return {
            "operationName": None,
            "variables": {},
            "query": query
        }

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

    @staticmethod
    def build_headers(Bearer, graphql=True):
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip',
            'authorization': f"Bearer {Bearer}",
            'content-type': 'application/json',
            'host': 'fennel-api.prod.fennel.com',
            'user-agent': 'Dart/3.3 (dart:io)',
        }
        if not graphql:
            headers['host'] = 'accounts.fennel.com'
        return headers
