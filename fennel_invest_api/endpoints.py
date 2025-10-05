class Endpoints:
    """Class for building URL request endpoints."""

    def __init__(self) -> None:
        """Initialize Endpoints class."""
        self.api = "https://api.fennel.com"

    def account_info_url(self) -> str:
        """Build URL for Account Info.

        Returns:
            Account Info URL as string.

        """
        return f"{self.api}/accounts/info"

    def portfolio_positions_url(self) -> str:
        """Build URL for Portfolio Positions.

        Returns:
            Portfolio Positions URL as string.

        """
        return f"{self.api}/portfolio/positions"

    def portfolio_cash_summary_url(self) -> str:
        """Build URL for Portfolio Cash Summary.

        Returns:
            Portfolio Cash Summary URL as string.

        """
        return f"{self.api}/portfolio/summary"

    def list_orders_url(self) -> str:
        """Build URL for Listing Orders.

        Returns:
            List Orders URL as string.

        """
        return f"{self.api}/orders/list"

    def get_order_url(self) -> str:
        """Build URL for Getting an Order.

        Returns:
            Get Order URL as string.

        """
        return f"{self.api}/order/get"

    def get_cancel_order_url(self) -> str:
        """Build URL for Canceling an Order.

        Returns:
            Cancel Order URL as string.

        """
        return f"{self.api}/order/cancel"

    def get_create_order_url(self) -> str:
        """Build URL for Creating an Order.

        Returns:
            Create Order URL as string.

        """
        return f"{self.api}/order/create"

    def get_prices_nbbo_url(self) -> str:
        """Build URL for NBBO Prices.

        Returns:
            NBBO Prices URL as string.

        """
        return f"{self.api}/markets/price/nbbo"

    def latest_prices_url(self) -> str:
        """Build URL for Latest Prices.

        Returns:
            Latest Prices URL as string.

        """
        return f"{self.api}/markets/prices/latest"

    @staticmethod
    def build_headers(bearer: str) -> dict[str, str]:
        """Build Request Headers.

        Returns:
            URL Headers as dictionary

        """
        return {
            "Authorization": f"Bearer {bearer}",
            "Accept": "application/x-protobuf",
            "Content-Type": "application/x-protobuf",
        }
