# tartiflette-asgi

ASGI adapter for [Tartiflette].

[tartiflette]: https://tartiflette.io

## Installation

Coming soon!

<!--
Assuming you have [Tartiflette installed](https://tartiflette.io/docs/tutorial/install-tartiflette), you can install `tartiflette-asgi` from PyPI:

```bash
pip install tartiflette-asgi
```
-->

## Usage

You can use the `TartifletteApp` ASGI application with any ASGI web framework.

For example, you can use [Starlette], which comes installed along with `tartiflette-asgi`:

[starlette]: https://www.starlette.io

```python
# main.py
from starlette.applications import Starlette
from tartiflette import Resolver

from tartiflette_asgi import TartifletteApp


@Resolver("Query.hello")
async def resolver_hello(parent, args, ctx, info):
    name = args["name"]
    return f"Hello, {name}!"


sdl = """
    type Query {
        hello(name: String): String
    }
"""

app = Starlette()
app.add_route("/graphql", TartifletteApp(sdl=sdl))

```

Serve the app using an ASGI web server, e.g. [uvicorn]:

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn main:app
```

You're now ready to make queries!

- From the command line using `curl`:

```bash
curl -X POST \
    -d '{"query": "query { hello(name: \"Chuck\") }"}' \
    -H "Content-Type: application/json" \
    http://localhost:8000/graphql
```

```json
{ "data": { "hello": "Hello, Chuck!" }, "errors": null }
```

- From Python using the `requests` library:

```python
import requests

r = requests.post(
    "http://localhost:8000/graphql",
    json={"query": "query { hello(name: 'Chuck') }"}
)
print(r.json())
```

```python
{
  "data": {
    "hello": "Hello, Chuck!"
  },
  "errors": None
}
```

- Using the built-in **GraphiQL client** by visiting [http://localhost:8000/graphql](http://localhost:8000/graphql) ✨:

![](https://github.com/florimondmanca/tartiflette-asgi/blob/master/img/graphiql.png)

It's just Tartiflette from there! Learn more by reading the [Tartiflette documentation][tartiflette].

## Development

Create a virtualenv and install dev dependencies:

```bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

## License

MIT
