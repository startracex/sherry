from types import FunctionType
from typing import Dict, List, Tuple, Optional
from .node import Node
from .requestcontext import RequestContext
from .response import Response


def parse_pattern(pattern: str) -> List[str]:
    vs = pattern.split("/")
    parts: List[str] = []
    for item in vs:
        if item != "":
            parts.append(item)
            if item[0] == "*":
                break
    return parts


def split_pattern(s: str) -> List[str]:
    return parse_pattern(s)


def split_slash(s: str) -> List[str]:
    vs = s.split("/")
    parts: List[str] = []
    for item in vs:
        if item != "":
            parts.append(item)
    return parts


class Router:
    root: Node
    handlers: Dict[str, Dict[str, List[FunctionType]]]

    def __init__(self):
        self.root = Node()
        self.handlers = {}

    def add_route(self, method: str, pattern: str, *handler_func: Tuple[FunctionType]):
        """
        add pattern to router

        method will be upper

        expand handler functions to handlers[pattern][method.upper()]
        """
        parts = parse_pattern(pattern)
        self.root.insert(pattern, parts, 0)
        if pattern not in self.handlers:
            self.handlers[pattern] = {}
        self.handlers[pattern][method.upper()] = list(handler_func)

    def get_route(self, path: str) -> tuple[Optional["Node"], Optional[dict]]:
        """
        parse path to pattern (split "/")

        get node and dynamic field mapping
        """
        search_parts = split_pattern(path)
        node = self.root.search(search_parts, 0)
        if node:
            params = {}
            parts = split_pattern(node.pattern)
            for index, part in enumerate(parts):
                if part[0] == ":":
                    params[part[1:]] = search_parts[index]
                if part[0] == "*" and len(part) > 1:
                    params[part[1:]] = "/".join(search_parts[index:])
                    break
            return node, params
        return None, None

    def handle(self, ctx: RequestContext) -> Response:
        """
        handle a request

        if no route defined, handle engine.no_route_handler

        if route defined, no method defined, handle engine.no_method_handler

        :param ctx: request
        :return: response handler's response
        """
        method = ctx.method()
        path = ctx.path()
        node, params = self.get_route(path)
        if node is not None:
            handlers = self.handlers.get(node.pattern).get(method)
            if handlers is not None:
                ctx.params = params
                ctx.handlers.extend(handlers)
            else:
                # has route, no method
                ctx.handlers.extend(ctx.engine.no_method_handler)
        else:
            # no route
            ctx.handlers.extend(ctx.engine.no_route_handler)
        # get response from ctx.next
        return ctx.next()
