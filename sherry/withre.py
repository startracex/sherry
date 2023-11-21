from typing import Dict, List, Optional
import re
from .response import Response
from .requestcontext import HandlerFunc, RequestContext


class WithRE:
    """
    match pattern with regex

    example
    ```
    engine = Engine(re=True)
    engine.add_route("GET", r"^/$", ...)
    ```
    """

    route_method_handlers: Dict[str, Dict[str, List["HandlerFunc"]]]

    def __init__(self):
        self.route_method_handlers = {}

    def handle(self, ctx: "RequestContext", trim_start: str) -> "Response":
        """
        handle a request

        if no route defined, handle engine.no_route_handler

        if route defined, no method defined, handle engine.no_method_handler

        content before len(trim_start) will not be in the match range

        :param ctx: request
        :param trim_start: trim start string
        :return: response handler's response
        """
        path = ctx.path()
        trim_path = path[len(trim_start) :]
        print(trim_path)
        method = ctx.method()
        pattern = self.get_match_pattern(trim_path)
        if pattern is None:
            # no route
            ctx.handlers.extend(ctx.engine.no_route_handler)
        else:
            handlers = self.get_match_handler(pattern, method)
            if handlers is None:
                # has route, no method
                ctx.handlers.extend(ctx.engine.no_method_handler)
            else:
                ctx.handlers.extend(handlers)
        return ctx.next()

    def add(self, method: str, pattern: str, *handlers):
        if pattern not in self.route_method_handlers:
            self.route_method_handlers[pattern] = {}
        self.route_method_handlers[pattern][method] = list(handlers)

    def get_match_pattern(self, path: str) -> str:
        for pattern in self.route_method_handlers:
            if re.match(pattern, path):
                return pattern
        return None

    def get_match_handler(
        self, pattern: str, method: str
    ) -> Optional[List["HandlerFunc"]]:
        if method in self.route_method_handlers[pattern]:
            return self.route_method_handlers[pattern][method]
        return None
