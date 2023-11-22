from typing import List, Tuple
from wsgiref.simple_server import make_server

from . import methods
from . import response
from .requestcontext import RequestContext, HandlerFunc
from .router import Router


class RouterGroup:
    engine: "Engine"
    parent: str
    prefix: str
    middlewares: Tuple["HandlerFunc"]

    def __init__(
        self,
        engine: "Engine" = None,
        prefix="",
        parent=None,
        *middlewares: "HandlerFunc",
    ):
        self.prefix = prefix
        self.middlewares = middlewares
        self.parent = parent
        self.engine = engine

    def group(self, prefix, *middlewares: "HandlerFunc"):
        """
        create router group
        """
        new_group = RouterGroup(
            prefix=self.prefix + prefix, parent=self, engine=self.engine
        )
        new_group.middlewares += middlewares
        self.engine.groups.append(new_group)
        return new_group

    def add_route(self, method, pattern, *handlers: HandlerFunc):
        """
        add a pattern to router
        """
        self.engine.router.add_route(method, self.prefix + pattern, *handlers)

    def get(self, pattern, *handlers):
        self.add_route(methods.GET, pattern, *handlers)

    def head(self, pattern, *handlers):
        self.add_route(methods.HEAD, pattern, *handlers)

    def post(self, pattern, *handlers):
        self.add_route(methods.POST, pattern, *handlers)

    def put(self, pattern, *handlers):
        self.add_route(methods.PUT, pattern, *handlers)

    def delete(self, pattern, *handlers):
        self.add_route(methods.DELETE, pattern, *handlers)

    def connect(self, pattern, *handlers):
        self.add_route(methods.CONNECT, pattern, *handlers)

    def options(self, pattern, *handlers):
        self.add_route(methods.OPTIONS, pattern, *handlers)

    def trace(self, pattern, *handlers):
        self.add_route(methods.TRACE, pattern, *handlers)

    def patch(self, pattern, *handlers):
        self.add_route(methods.PATCH, pattern, *handlers)

    def all(self, pattern, *handlers):
        for method in methods.ALL:
            self.add_route(method, pattern, *handlers)

    def no_route(self, *handlers):
        """
        set no route handler
        """
        self.engine.no_route_handler = list(handlers)

    def no_method(self, *handlers):
        """
        set no method handler
        """
        self.engine.no_method_handler = list(handlers)

    def use(self, *middlewares):
        """
        use middlewares before handlers
        """
        self.middlewares += middlewares


class Engine(RouterGroup):
    router_group: "RouterGroup"
    router: "Router"
    prefix: str
    middlewares = []
    groups: List["RouterGroup"]
    engine: "Engine"
    no_route_handler: List["HandlerFunc"]
    no_method_handler: List["HandlerFunc"]

    def __init__(self, re=False, base=""):
        self.router_group = RouterGroup(engine=self)
        self.engine = self
        self.no_method_handler = [response.error_method_not_allow]
        self.no_route_handler = [response.error_not_found]
        self.prefix = "" if base == "/" else base
        self.groups = []
        self.router = Router()
        if re:
            self.use_regex()

    def use_regex(self):
        self.router.re = True

    def run(
        self,
        port: int,
        addr="localhost",
        fmt="Running on http://{addr}:{port}",
        poll_interval: float = 0.5,
    ):
        """
        start a http server
        """
        httpd = make_server(addr, port, self.serve_http)
        print(fmt.format(addr=addr, port=port))
        httpd.serve_forever(poll_interval=poll_interval)

    def serve_http(self, env, start_response):
        """
        serve http request
        """
        middlewares = self.middlewares
        ctx = RequestContext(env, self.engine)
        path = ctx.path()
        prefix = ""

        for group in self.groups:
            print("group.prefix", group.prefix)
            if path.startswith(group.prefix + "/"):
                prefix = group.prefix
                middlewares += group.middlewares

        ctx.handlers = list(middlewares)
        if self.router.re:
            handle_response = self.router.handle_prefix(ctx, prefix)
        else:
            handle_response = self.router.handle(ctx)

        return handle_response.start_response(start_response)
