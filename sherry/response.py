import json
from wsgiref.headers import Headers
from .utils import http_status_text


class Response:
    response: bytes
    _status: int
    charset: str
    headers: "Headers"

    def __init__(
        self, response: bytes = None, status=200, charset="utf-8", header=None
    ):
        self.response = response
        self.charset = charset
        self.headers = Headers() if header is None else header
        if charset:
            self.headers.add_header("charset", charset)
        self._status = status

    def status(self, code):
        """
        set http status

        :param code: status
        """
        self._status = code

    def write(self, data: bytes):
        """
        set response data (bytes)

        :param data: response data
        """
        self.response = data

    def string(self, s: str):
        """
        set response data (format string)

        :param s: format string
        """
        self.write(s.encode(self.charset))

    def json(self, data, **params):
        """
        set response data (json)
        """
        self.content_type("application/json")
        self.string(json.dumps(data, **params))

    def set_header(self, key: str, value: str):
        self.headers.add_header(key, value)

    def content_type(self, content_type: str):
        """
        add header Content-Type
        """
        self.set_header("content-type", content_type)

    def content_length(self, length: int):
        """
        add header Content-Length
        """
        self.set_header("content-length", length)

    def start_response(self, start_response):
        start_response(
            f"{self._status} {http_status_text(self._status)}", self.headers.items()
        )
        if self.response:
            if isinstance(self.response, bytes):
                yield self.response
            else:
                yield self.response.encode(self.charset)


def error_not_found() -> Response:
    return response_status_text(404)


def error_method_not_allow() -> Response:
    return response_status_text(405)


def response_status_text(code=200) -> Response:
    return Response(http_status_text(code).encode(), code)
