# tartiflette-starlette

[![travis](https://img.shields.io/travis/tartiflette/tartiflette-starlette.svg)](https://travis-ci.org/tartiflette/tartiflette-starlette)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
[![pypi](https://img.shields.io/pypi/v/tartiflette-starlette.svg)][pypi-url]
![license](https://img.shields.io/badge/license-MIT-green.svg)

[pypi-url]: https://pypi.org/project/tartiflette-starlette/

[Starlette]-powered [ASGI] adapter for [Tartiflette], the Python asynchronous GraphQL engine.

> **Tip**: although it relies on Starlette for HTTP request processing, **`tartiflette-starlette` can be used with any ASGI web framework** that supports mounting ASGI sub-applications.

> ⚠️ This package is still under development. Remember to pin your dependencies!

[asgi]: https://asgi.readthedocs.io/
[starlette]: https://www.starlette.io
[tartiflette]: https://tartiflette.io

## Installation

Just like Tartiflette, `tartiflette-starlette` requires Python 3.6+.

PyPI package is coming soon!

<!--
Assuming you have [Tartiflette installed](https://tartiflette.io/docs/tutorial/install-tartiflette), you can install `tartiflette-starlette` from PyPI:

```bash
pip install tartiflette-starlette
```
-->

## Usage

The `TartifletteApp` class provided by `tartiflette-starlette` is an ASGI3-compliant application. As such, it can be served on its own by an ASGI web server, or mounted on another ASGI application.

The following example adds a `TartifletteApp` GraphQL endpoint to a Starlette application at `/graphql`:

```python
# main.py
from starlette.applications import Starlette
from tartiflette import Resolver

from tartiflette_starlette import TartifletteApp

# Create a Tartiflette resolver for the `hello` field.
@Resolver("Query.hello")
async def resolve_hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"

# Define the schema using an SDL string.
# Note: Tartiflette also has support for `.graphql` files.
# See: https://tartiflette.io/docs/api/engine
sdl = """
    type Query {
        hello(name: String): String
    }
"""

app = Starlette()
app.add_route("/graphql", TartifletteApp(sdl=sdl))
```

Serve it using any ASGI web server — let's use [uvicorn]:

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn main:app
```

You're now ready to make GraphQL queries!

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

- Using the built-in **GraphiQL client** by visiting [http://localhost:8000/graphql](http://localhost:8000/graphql) from your browser ✨

![](https://github.com/tartiflette/tartiflette-starlette/blob/master/img/graphiql.png?raw=true)

It's just Tartiflette from there! Learn more by reading the [Tartiflette documentation][tartiflette].

## API Reference

### `tartiflette_starlette.TartifletteApp`

#### Parameters

**Note**: all parameters are keyword-only.

- `engine (Engine)`: a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl (str)`: a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `graphiql (bool)`: whether to serve the GraphiQL when accessing the endpoint via a web browser. Defaults to `True`.
- `schema_name (str)`: name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

#### Methods

- `__call__(scope, receive, send)`: implementation of the ASGI3 callable interface.

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-starlette/tree/master/CONTRIBUTING.md).

## License

MIT
