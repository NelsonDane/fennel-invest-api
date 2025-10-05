from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Concatenate, Literal, ParamSpec, TypeVar

import requests

from fennel_invest_api.endpoints import Endpoints

# If these are all red/errored, run "make" to regenerate the protobuf files.
from fennel_invest_api.models.account_id_pb2 import AccountIDRequest
from fennel_invest_api.models.accounts_pb2 import Account, AccountsResponse
from fennel_invest_api.models.cancel_order_pb2 import CancelOrderRequest
from fennel_invest_api.models.create_order_pb2 import CreateOrderRequest
from fennel_invest_api.models.get_order_pb2 import GetOrderRequest
from fennel_invest_api.models.list_orders_pb2 import ListOrdersRequest, ListOrdersResponse, Order
from fennel_invest_api.models.nbbo_pb2 import NbboRequest, NbboResponse
from fennel_invest_api.models.order_details_pb2 import OrderType, RoutingOption, Side, TimeInForce
from fennel_invest_api.models.order_response_pb2 import OrderResponse
from fennel_invest_api.models.portfolio_summary_pb2 import PortfolioSummaryResponse
from fennel_invest_api.models.positions_pb2 import Position, PositionsResponse
from fennel_invest_api.models.prices_pb2 import MultiPriceRequest, MultiPriceResponse, PriceResponse
from fennel_invest_api.utils import FennelAPIError, InvalidBearerTokenError, MissingBearerError

P = ParamSpec("P")
R = TypeVar("R")


def check_login(func: Callable[Concatenate["Fennel", P], R]) -> Callable[Concatenate["Fennel", P], R]:
    """Ensure Bearer token is valid before authenticated request.

    Returns:
        The decorated function callable.

    """

    @wraps(func)
    def wrapper(self: "Fennel", *args: P.args, **kwargs: P.kwargs) -> R:
        if not self.Bearer:
            raise MissingBearerError
        return func(self, *args, **kwargs)

    return wrapper


class Fennel:
    """Object to interact with the Fennel API. One object per account/token."""

    def __init__(self, pat_token: str) -> None:
        """Initialize Fennel API connection.

        Raises:
            InvalidBearerTokenError: If the Bearer token is invalid.

        """
        self.session = requests.Session()
        self.endpoints = Endpoints()
        self.timeout = 10
        self.Bearer = pat_token
        self.headers = self.endpoints.build_headers(self.Bearer)
        # Ensure bearer is valid
        try:
            self.get_account_info()
        except FennelAPIError as e:
            raise InvalidBearerTokenError from e

    # region Accounts
    # https://api.fennel.com/docs#tag/Accounts

    @check_login
    def get_account_info(self) -> list[Account]:
        """Get Fennel Account Info: https://api.fennel.com/docs#tag/Accounts/operation/info_accounts_info_get.

        Returns:
            list[Account]: A list of accounts associated with the API token.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.get(
            url=self.endpoints.account_info_url(),
            headers=self.headers,
            timeout=self.timeout,
        )
        if not response.ok:
            msg = f"Account ID Check failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = AccountsResponse()
        response_proto.ParseFromString(response.content)
        return sorted(response_proto.accounts, key=lambda x: x.name)

    # region: Portfolio
    # https://api.fennel.com/docs#tag/Portfolio

    @check_login
    def get_portfolio_positions(self, account_id: str) -> list[Position]:
        """Get Fennel Positions for a specific account: https://api.fennel.com/docs#tag/Portfolio/operation/positions_portfolio_positions_post.

        Returns:
            list[Position]: A list of positions for the specified account.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.post(
            url=self.endpoints.portfolio_positions_url(),
            headers=self.headers,
            data=AccountIDRequest(account_id=account_id).SerializeToString(),
        )
        if not response.ok:
            msg = f"Portfolio Positions Request failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = PositionsResponse()
        response_proto.ParseFromString(response.content)
        return list(response_proto.positions)

    @check_login
    def get_portfolio_cash_summary(self, account_id: str) -> PortfolioSummaryResponse:
        """Get Fennel Cash Summary for a specific account: https://api.fennel.com/docs#tag/Portfolio/operation/cash_summary_portfolio_summary_post.

        Returns:
            PortfolioSummaryResponse: The cash summary for the specified account.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.post(
            url=self.endpoints.portfolio_cash_summary_url(),
            headers=self.headers,
            data=AccountIDRequest(account_id=account_id).SerializeToString(),
        )
        if not response.ok:
            msg = f"Portfolio Cash Summary Request failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = PortfolioSummaryResponse()
        response_proto.ParseFromString(response.content)
        return response_proto

    # region: Prices
    # https://api.fennel.com/docs#tag/Prices

    @check_login
    def get_latest_prices(self, symbols: list[str]) -> list[PriceResponse]:
        """Get Latest Prices for a list of symbols: https://api.fennel.com/docs#tag/Prices/operation/latest_prices_markets_prices_latest_post.

        Returns:
            list[PriceResponse]: A list of latest prices for the specified symbols.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        search_response = self.session.post(
            url=self.endpoints.latest_prices_url(),
            headers=self.headers,
            data=MultiPriceRequest(symbols=symbols).SerializeToString(),
        )
        if not search_response.ok:
            msg = f"Stock Search Request failed with status code {search_response.status_code}: {search_response.text}"
            raise FennelAPIError(msg)
        search_response_proto = MultiPriceResponse()
        search_response_proto.ParseFromString(search_response.content)
        return list(search_response_proto.prices)

    @check_login
    def get_prices_nbbo(self, symbol: str) -> NbboResponse:
        """Get Latest NBBO Prices for a specific symbol: https://api.fennel.com/docs#tag/Prices/operation/nbbo_markets_price_nbbo_post.

        Returns:
            NbboResponse: The NBBO prices for the specified symbol.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.post(
            url=self.endpoints.get_prices_nbbo_url(),
            headers=self.headers,
            data=NbboRequest(symbol=symbol).SerializeToString(),
        )
        if not response.ok:
            msg = f"NBBO Request failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = NbboResponse()
        response_proto.ParseFromString(response.content)
        return response_proto

    # region: Orders
    # https://api.fennel.com/docs#tag/Orders

    @check_login
    def list_orders(self, account_id: str, since_date: datetime) -> list[Order]:
        """List all orders for a specific account: https://api.fennel.com/docs#tag/Orders/operation/list_orders_orders_list_post.

        Returns:
            list[Order]: A list of orders for the specified account.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.post(
            url=self.endpoints.list_orders_url(),
            headers=self.headers,
            data=ListOrdersRequest(account_id=account_id, since_date=since_date).SerializeToString(),
        )
        if not response.ok:
            msg = f"List Orders Request failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = ListOrdersResponse()
        response_proto.ParseFromString(response.content)
        return list(response_proto.orders)

    @check_login
    def get_order(self, order_id: str) -> Order:
        """Get details of a specific order: https://api.fennel.com/docs#tag/Orders/operation/get_order_orders_get.

        Returns:
            Order: The order details.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.post(
            url=self.endpoints.get_order_url(),
            headers=self.headers,
            data=GetOrderRequest(order_id=order_id).SerializeToString(),
        )
        if not response.ok:
            msg = f"Get Order Request failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = Order()
        response_proto.ParseFromString(response.content)
        return response_proto

    @check_login
    def cancel_order(self, order_id: str) -> OrderResponse:
        """Cancel a specific order: https://api.fennel.com/docs#tag/Orders/operation/cancel_order_orders_cancel_post.

        Returns:
            OrderResponse: The response from the API or an error message.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)

        """
        response = self.session.post(
            url=self.endpoints.get_cancel_order_url(),
            headers=self.headers,
            data=CancelOrderRequest(order_id=order_id).SerializeToString(),
        )
        if not response.ok:
            msg = f"Cancel Order Request failed with status code {response.status_code}: {response.text}"
            raise FennelAPIError(msg)
        response_proto = OrderResponse()
        response_proto.ParseFromString(response.content)
        return response_proto

    @check_login
    def place_order(  # noqa: PLR0913, PLR0917
        self,
        account_id: str,
        symbol: str,
        shares: float,
        side: Literal["BUY", "SELL"],
        order_type: Literal["MARKET", "LIMIT"] = "MARKET",
        limit_price: float | None = None,
        time_in_force: Literal["DAY"] = "DAY",
        route: Literal["EXCHANGE", "EXCHANGE_ATS", "EXCHANGE_ATS_SDP", "QUIK"] = "EXCHANGE",
    ) -> OrderResponse:
        """Place an order for a specific account: https://api.fennel.com/docs#tag/Orders/operation/create_order_order_create_post.

        Returns:
            OrderResponse: The response from the API or an error message.

        Raises:
            FennelAPIError: If API call fails (doesn't return 200)
            ValueError: If parameters are invalid.

        """
        # Verify parameters
        if shares <= 0:
            msg = "Shares must be greater than 0"
            raise ValueError(msg)
        if limit_price is not None and limit_price <= 0:
            msg = "Limit price must be greater than 0"
            raise ValueError(msg)
        if order_type == "LIMIT" and limit_price is None:
            msg = "Limit price must be provided for limit orders"
            raise ValueError(msg)
        # Validate side
        try:
            side_int = Side.Value(side)
            side_enum = Side.Name(side_int)
        except ValueError as e:
            msg = f'Invalid side: {side}. Must be "BUY" or "SELL".'
            raise ValueError(msg) from e
        # Validate order type
        try:
            order_type_int = OrderType.Value(order_type)
            order_type_enum = OrderType.Name(order_type_int)
        except ValueError as e:
            msg = f'Invalid order type: {order_type}. Must be "MARKET" or "LIMIT".'
            raise ValueError(msg) from e
        # Validate time in force
        try:
            time_in_force_int = TimeInForce.Value(time_in_force)
            time_in_force_enum = TimeInForce.Name(time_in_force_int)
        except ValueError as e:
            msg = f'Invalid time in force: {time_in_force}. Must be "DAY".'
            raise ValueError(msg) from e
        # Validate route
        try:
            route_int = RoutingOption.Value(route)
            route_enum = RoutingOption.Name(route_int)
        except ValueError as e:
            msg = f'Invalid route: {route}. Must be "EXCHANGE", "EXCHANGE_ATS", "EXCHANGE_ATS_SDP", or "QUIK".'
            raise ValueError(msg) from e
        # Create order
        order_request = CreateOrderRequest(
            account_id=account_id,
            symbol=symbol,
            shares=shares,
            limit_price=limit_price,
            side=side_enum,
            type=order_type_enum,
            time_in_force=time_in_force_enum,
            route=route_enum,
        )
        order_response = self.session.post(
            self.endpoints.get_create_order_url(),
            headers=self.headers,
            data=order_request.SerializeToString(),
        )
        if not order_response.ok:
            msg = f"Order Request failed with status code {order_response.status_code}: {order_response.text}"
            raise FennelAPIError(msg)
        order_response_proto = OrderResponse()
        order_response_proto.ParseFromString(order_response.content)
        return order_response_proto
