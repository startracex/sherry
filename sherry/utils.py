import http
from types import FunctionType


def execute_func(func: FunctionType, *args, **kwargs) -> FunctionType:
    args_needed = func.__code__.co_argcount

    if args_needed > len(args):
        args += (None,) * (args_needed - len(args))

    if args_needed < len(args):
        args = args[:args_needed]

    return func(*args, **kwargs)


def http_status_text(status) -> str:
    """
    return status' phrase
    """
    return http.HTTPStatus(status).phrase
