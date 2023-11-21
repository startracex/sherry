from types import FunctionType
from typing import List
from ..engine import RouterGroup
from .. import methods
from ..requestcontext import HandlerFunc


def handler(pattern: str, methods_list: List[str], group: "RouterGroup"):
    """
    wrap a handler call add_route

    example
    ```py
    app = Engine()
    # function decorators
    @handler("/", ["GET"], app)
    def index_handler():
        pass
    # as
    app.add_route("GET", "/", index_handler)

    # class decorators
    @handler("/", ["GET"], app)
    class Pages:
        def middle_handler():
            pass
        def index_handler():
            pass
    # as
    engine.add_route("GET", Pages.middle_handler, Pages.index_handler)
    """

    def decorators(var: HandlerFunc | type):
        if group:
            for method in methods_list:
                handlers = ()

                if isinstance(var, FunctionType):
                    handlers = (var,)

                elif isinstance(var, type):
                    members = vars(var)
                    for member in members:
                        attr = getattr(var, member)
                        if callable(attr):
                            handlers += (attr,)

                if len(handlers):
                    group.add_route(method, pattern, *handlers)

    return decorators


def get(pattern: str, group: "RouterGroup"):
    """
    wrap a handler call get

    example
    ```
    @get("/")
    def index_handler(req, res):
        pass
    # as
    app.get("/", index_handler)
    ```
    """
    return handler(pattern, [methods.GET], group)


def head(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.HEAD], group)


def post(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.POST], group)


def put(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.PUT], group)


def delete(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.DELETE], group)


def connect(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.CONNECT], group)


def options(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.OPTIONS], group)


def trace(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.TRACE], group)


def patch(pattern: str, group: "RouterGroup"):
    return handler(pattern, [methods.PATCH], group)


def all(pattern: str, group: "RouterGroup"):
    return handler(pattern, methods.ALL, group)
