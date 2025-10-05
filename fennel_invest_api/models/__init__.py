# type: ignore
"""Fennel Invest API Models. Generated from: https://api.fennel.com/docs#tag/Get-Started"""

import importlib

__all__ = [
    "account_id_pb2",
    "accounts_pb2",
    "cancel_order_pb2",
    "create_order_pb2",
    "exception_pb2",
    "get_order_pb2",
    "list_orders_pb2",
    "nbbo_pb2",
    "order_details_pb2",
    "order_response_pb2",
    "portfolio_summary_pb2",
    "position_pb2",
    "prices_pb2",
]


# Lazy load submodules
def __getattr__(name: str):
    if name in __all__:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
