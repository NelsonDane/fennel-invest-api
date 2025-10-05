class MissingBearerError(Exception):
    """Exception raised when a request is made with a missing Bearer token."""

    def __init__(self) -> None:
        """Initialize MissingBearerError Exception."""
        self.message = "Bearer token is not set. Please login first."
        super().__init__(self.message)


class InvalidBearerTokenError(Exception):
    """Exception raised when a token results in an invalid or blank response."""

    def __init__(self) -> None:
        """Initialize InvalidBearerTokenError Exception."""
        self.message = "Invalid Bearer token. Please check that your token is valid."
        super().__init__(self.message)


class FennelAPIError(Exception):
    """Exception raised when an API request does not return 200."""

    def __init__(self, msg: str) -> None:
        """Initialize FennelAPIError Exception."""
        super().__init__(msg)
