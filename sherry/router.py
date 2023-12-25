import re
from types import FunctionType
from typing import Dict, List, Optional

from .node import Node, wild_of
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
    re: bool

    def __init__(self):
        self.root = Node()
        self.handlers = {}
        self.re = False

    def add_route(self, method: str, pattern: str, *handler_func: FunctionType):
        """
        add pattern to router

        method will be upper

        expand handler functions to handlers[pattern][method.upper()]
        """
        if not self.re:
            self.root.set(pattern)
        if pattern not in self.handlers:
            self.handlers[pattern] = {}
        self.handlers[pattern][method.upper()] = list(handler_func)

    def get_route(self, path: str) -> tuple[Optional["Node"], Optional[dict]]:
        """
        parse path to pattern (split "/")

        get node and dynamic field mapping
        """
        search_parts = split_pattern(path)
        node = self.root.get(path)
        if node:
            params = {}
            parts = split_pattern(node.pattern)
            for index, part in enumerate(parts):
                is_wild, wild_key, is_multi = wild_of(part)
                if is_wild:
                    if is_multi:
                        params[wild_key] = "/".join(search_parts[index:])
                        break
                    else:
                        params[wild_key] = search_parts[index]

            return node, params

        return None, None

    def handle(self, ctx: RequestContext) -> Response:
        """
        handle a request

        if no route defined, handle engine.no_route_handler

        if route defined, no method defined, handle engine.no_method_handler

        :param ctx: request context
        :return: response handler's response
        """

        node, params = self.get_route(ctx.path())
        ctx.params = params
        if node is not None:
            # has router
            pattern = node.pattern
            method = ctx.method()

            h_p = self.handlers.get(pattern)
            # if h_p:
            h_p_m = h_p.get(method)
            if h_p_m:
                # has method
                ctx.handlers.extend(h_p_m)
            else:
                # no method
                ctx.handlers.extend(ctx.engine.no_method_handler)
        else:
            # no route
            ctx.handlers.extend(ctx.engine.no_route_handler)

        return ctx.next()

    def handle_prefix(self, ctx: RequestContext, prefix: str) -> Response:
        """
        handle a request

        if no route defined, handle engine.no_route_handler

        if route defined, no method defined, handle engine.no_method_handler

        :param ctx: request
        :param prefix: group prefix
        :return: response handler's response
        """
        path = ctx.path()
        method = ctx.method()
        for regex in self.handlers:
            if len(regex) < len(prefix) or len(regex[: len(prefix)]) < len(prefix):
                continue
            if re.match(regex[len(regex):], path[len(regex):]):
                key = prefix + regex
                handlers_map = self.handlers.get(key)
                handlers = handlers_map.get(method)
                if handlers is None:
                    ctx.handlers.extend(ctx.engine.no_method_handler)
                else:
                    ctx.handlers.extend(handlers)
                return ctx.next()

        ctx.handlers.extend(ctx.engine.no_route_handler)
        return ctx.next()
