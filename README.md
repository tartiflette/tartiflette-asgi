# tartiflette-starlette

[![travis](https://img.shields.io/travis/tartiflette/tartiflette-starlette.svg)](https://travis-ci.org/tartiflette/tartiflette-starlette)
[![black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/ambv/black)
![python](https://img.shields.io/pypi/pyversions/tartiflette-starlette.svg)
[![pypi](https://img.shields.io/pypi/v/tartiflette-starlette.svg)](https://pypi.org/project/tartiflette-starlette/)
![license](https://img.shields.io/badge/license-MIT-green.svg)

A [Starlette]-powered [ASGI] adapter for the [Tartiflette] GraphQL engine.

[asgi]: https://asgi.readthedocs.io/
[starlette]: https://www.starlette.io
[tartiflette]: https://tartiflette.io

> ⚠️ This package is still under development. Be sure to pin your dependencies!

## Installation

Assuming [you have already installed Tartiflette](https://tartiflette.io/docs/tutorial/install-tartiflette), you can install `tartiflette-starlette` from PyPI:

```bash
pip install tartiflette-starlette
```

**Note**: `tartiflette-starlette` is compatible with Starlette 0.12+.

## Usage

> Getting started with Tartiflette or GraphQL? See [Resources](#resources).

The `TartifletteApp` class provided by `tartiflette-starlette` is an ASGI3-compliant application. As such, it can be served on its own using any ASGI web server, or it can be mounted onto another ASGI application.

**Note**: GraphQL subscriptions are not supported yet.

### Create an ASGI GraphQL app

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
# Note: Tartiflette also supports `.graphql` files.
# See: https://tartiflette.io/docs/api/engine
sdl = """
    type Query {
        hello(name: String): String
    }
"""

app = TartifletteApp(sdl=sdl)
```

> **Note**: the GraphQL endpoint is exposed on the `/graphql` path by default.

### Serve the app

A `TartifletteApp` can be served using any ASGI web server, e.g. [uvicorn]:

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn graphql:app
```

### Make GraphQL queries

As per the [GraphQL spec](https://graphql.org/learn/serving-over-http/#http-methods-headers-and-body), the GraphQL query can be passed in various ways:

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

### Interactive GraphiQL client

You can use the built-in GraphiQL client available at [http://localhost:8000/graphql](http://localhost:8000/graphql) to interactively make queries in the browser. ✨

![](https://github.com/tartiflette/tartiflette-starlette/raw/master/img/graphiql.png)

### Mouting onto an ASGI application

Most async web frameworks provide a way to add a route to another ASGI application. This allows you to serve a `TartifletteApp` along with other endpoints.

When doing so, use `root=True`:

```python
# graphql.py
app = TartifletteApp(..., root=True)
```

This allows you to mount the GraphQL app anywhere on the parent ASGI app. For example, with Starlette:

```python
# main.py
from starlette.applications import Starlette
from graphql import app as graphql_app

app = Starlette()
app.mount("/graphql", graphql_app)
```

Run `$ uvicorn main:app` and make requests at `http://localhost:8000/graphql`.

### Accessing request information

The Starlette `Request` object is made available in the Tartiflette `context` which, for example, you can access from resolvers:

```python
@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info) -> str:
    request = context["request"]
    user = getattr(request.state, "user", None)
    return "a mystery" if user is None else user
```

## Resources

Once a `TartifletteApp` is setup, it's just Tartiflette and GraphQL from there!

Here are a few resources you may find useful when getting started:

- [Introduction to GraphQL](https://graphql.org/learn/): an overview of the GraphQL language.
- [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/getting-started): a step-by-step guide to building your first Tartiflette app.
- [Tartiflette API reference](https://tartiflette.io/docs/api/engine): learn about core concepts such as engines, resolvers, mutations, etc.

Happy querying!

## API Reference

### `tartiflette_starlette.TartifletteApp`

#### Parameters

**Note**: all parameters are keyword-only.

- `engine (Engine)`: a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl (str)`: a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `graphiql (bool)`: whether to serve the GraphiQL when accessing the endpoint via a web browser. Defaults to `True`.
- `path (str)`: the path which clients should make GraphQL queries to. Defaults to `"/graphql"`.
- `root (bool)`: shortcut for `path=""`. Defaults to `False`.
- `schema_name (str)`: name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

#### Methods

- `__call__(scope, receive, send)`: implementation of the ASGI3 callable interface.

#### Error responses

| Status code                | Description                                               |
| -------------------------- | --------------------------------------------------------- |
| 405 Method Not Allowed     | The HTTP method is not one of `GET`, `HEAD` or `POST`.    |
| 415 Unsupported Media Type | A POST request was made with an unsupported media type.   |
| 400 Bad Request            | The GraphQL query could not be found in the request data. |

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-starlette/tree/master/CONTRIBUTING.md).

## Changelog

Changes to this project are recorded in the [changelog](https://github.com/tartiflette/tartiflette-starlette/tree/master/CHANGELOG.md).

## License

MIT
