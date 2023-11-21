import urllib.parse
from typing import List, Optional, TYPE_CHECKING
from .response import Response
from .utils import execute_func

if TYPE_CHECKING:
    from .engine import Engine


class HandlerFunc:
    def __call__(
        self, _1: Optional["Request"], _2: Optional["Response"]
    ) -> Optional[Response]:
        pass


class RequestContext:
    handlers: List["HandlerFunc"]
    _index: int
    response: Response
    engine: "Engine"
    params: Optional[dict]

    def __init__(self, environ, engine=None):
        self.engine = engine
        self._environ = environ
        self._index = -1
        self.handlers = []

    def next(self) -> Response:
        """
        increase index, call next handler function
        :return: response
        """
        self._index += 1
        self.response = Response()
        while self._index < len(self.handlers):
            next_func = self.handlers[self._index]
            has_return = execute_func(next_func, self, self.response)
            if has_return:
                # has return, response is from return value
                if isinstance(has_return, Response):
                    # response is Response
                    self.response = has_return
                else:
                    # encode response to Response
                    self.response = Response(str(has_return).encode())
            self._index += 1
        return self.response

    def abort(self):
        """
        abort at current handler
        """
        self._index = len(self.handlers)

    def reset(self):
        """
        reset handlers index
        """
        self._index = -1

    def method(self) -> str:
        """
        get http method
        """
        return self._environ["REQUEST_METHOD"]

    def server_port(self) -> str:
        """
        get port
        """
        return self._environ["SERVER_PORT"]

    def path(self) -> str:
        """
        get url path
        """
        return self._environ["PATH_INFO"]

    def query_string(self):
        """
        get query string
        """
        return self._environ["QUERY_STRING"]

    def content_length(self):
        """
        get content-length
        """
        return self._environ["CONTENT_LENGTH"]

    def content_type(self):
        """
        get content-type
        """
        return self._environ["CONTENT_TYPE"]

    def headers(self):
        """
        get headers
        """
        return self._environ["HTTP_ACCEPT"]

    @property
    def query(self):
        """
        get query arguments
        """
        get_arguments = urllib.parse.parse_qs(self._environ["QUERY_STRING"])
        return {k: v[0] for k, v in get_arguments.items()}


Request = RequestContext
"""
alias of RequestContext
"""
