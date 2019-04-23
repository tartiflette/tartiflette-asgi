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

The `TartifletteApp` class provided by `tartiflette-starlette` is an ASGI3-compliant application. As such, it can be served on its own by an ASGI web server, or mounted onto another ASGI application.

It's just Tartiflette from there! Learn more by reading the [Tartiflette documentation][tartiflette].

### Creating a GraphQL app

The following example defines a standalone `TartifletteApp` which exposes the GraphQL endpoint at `/graphql`:

```python
# graphql.py
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

app = TartifletteApp(sdl=sdl, path="/graphql")
```

### Serving the app

Since `TartifletteApp` is an ASGI application, it can be served using any ASGI web server, e.g. [uvicorn]:

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn graphql:app
```

### Making GraphQL queries

Once the server is running, we're ready to make queries.

As per the [GraphQL spec](https://graphql.org/learn/serving-over-http/#http-methods-headers-and-body), the query can be passed in various ways:

- **URL query string** (methods: `GET`, `POST`):

```bash
curl 'http://localhost:8000/graphql?query=\{hello(name:"Chuck")\}'
```

- **JSON-encoded body** (methods: `POST`):

```bash
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ hello(name: \"Chuck\") }"}' \
  http://localhost:8000/graphql
```

- **Raw body** (methods: `POST`):

```bash
curl \
  -X POST \
  -H "Content-Type: application/graphql" \
  -d '{ hello(name: "Chuck") }' \
  http://localhost:8000/graphql
```

All these requests result in the same response:

```json
{
  "data": { "hello": "Hello, Chuck!" },
  "errors": null
}
```

Furthermore, you can use the built-in **GraphiQL client**: visit [http://localhost:8000/graphql](http://localhost:8000/graphql) to interactively make queries in the browser. ✨

![](https://github.com/tartiflette/tartiflette-starlette/blob/master/img/graphiql.png?raw=true)

### Mouting onto an ASGI application

A `TartifletteApp` can be easily mounted onto another ASGI application. This allows you to make it available along with other endpoints.

The following example mounts the GraphQL app from [Creating a GraphQL app](#creating-a-graphql-app) onto a Starlette application:

```python
# main.py
from starlette.applications import Starlette
from graphql import app as graphql_app

app = Starlette()
app.mount("/", graphql_app)
```

You can serve it using `uvicorn main:app` and make requests at `http://localhost:8000/graphql` as previously.

### Accessing request information

The Starlette `Request` object is made available in the Tartiflette `context` which, for example, you can access from resolvers:

```python
@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info) -> str:
    request = context["request"]
    user = getattr(request.state, "user", None)
    return "a mystery" if user is None else user
```

## API Reference

### `tartiflette_starlette.TartifletteApp`

#### Parameters

**Note**: all parameters are keyword-only.

- `engine (Engine)`: a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl (str)`: a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `graphiql (bool)`: whether to serve the GraphiQL when accessing the endpoint via a web browser. Defaults to `True`.
- `path (str)`: the path which clients should make GraphQL queries to. Defaults to `"/"`. A popular alternative is `"/graphql"`.
- `schema_name (str)`: name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

#### Methods

- `__call__(scope, receive, send)`: implementation of the ASGI3 callable interface.

#### Error responses

| Status code                | Description                                               |
| -------------------------- | --------------------------------------------------------- |
| 405 Method Not Allowed     | The HTTP method is not one of `GET`, `HEAD` and `POST`.   |
| 415 Unsupported Media Type | A POST request was made with an unsupported media type.   |
| 400 Bad Request            | The GraphQL query could not be found in the request data. |

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-starlette/tree/master/CONTRIBUTING.md).

## Changelog

Changes to this project are recorded in the [changelog](https://github.com/tartiflette/tartiflette-starlette/tree/master/CHANGELOG.md).

## License

MIT
