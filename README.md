# sherry

Python web framework

```sh
pip install sherry
```

## Simple application

```py
from sherry import Sherry, get, Request

hi_str = "hi {}"
app = Sherry()


@get("/", app)
def hello_world(request: Request):
    return hi_str.format(request.query["name"] or "world")


app.run(9527)
```

## Create application engine

```py
from sherry import Sherry, Engine

app1 = Sherry()
# or
app2 = Engine()
# with regex
app3 = Engine(re=True)
```

## Add handlers

### Create handler

If a return value exists for the function, it will be converted to a response (if not)

```py
def my_handler(*args, **kwargs) -> Response | Any:
    pass
```

If there is no return value, the response will be the response field of the first parameter

The second parameter is the response field of the first parameter

```py
from sherry import Request, Response


def my_handler(ctx: Request) -> None:
    pass


def my_handler(req: Request, res: Response) -> None:
    """
    req.response == res # True
    """
    pass
```

### Add route, method, handlers

```py
app = Engine()
app.add_route("GET" """http method""", "/" """pattern""", handlers)
app.add_route("GET", "/:some" """match one dynamic""", handlers)
app.add_route("GET", "/xx/*any" """match multiple dynamic""", handlers)
```

with regex

```py
app = Engine(re=True)
app.add_route("GET", "^/\d$" """match one number""", handlers)
```

### Wrapping

```py
app.get("/", handlers)
app.post("/", handlers)
...
```

## Decorators

```py
from sherry.decorators import handler, get  # ...


@handler("/" """pattern""", ["GET" """"http methods"""], app)
def func():
    pass


@get("/"  """pattern""", app)
def func():
    pass
```

example

```py
from sherry import Engine, handler

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
app.add_route("GET", Pages.middle_handler, Pages.index_handler)
```
