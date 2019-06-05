<div align="center">
  <img src="https://user-images.githubusercontent.com/158689/58954519-b05ad680-8799-11e9-9134-90622e7731f3.png" alt="tartiflette-starlette logo"/>
</div>

<p align="center">
  <a href="https://travis-ci.org/tartiflette/tartiflette-starlette">
    <img src="https://img.shields.io/travis/tartiflette/tartiflette-starlette.svg" alt="Build status">
  </a>
  <a href="https://pypi.org/project/tartiflette-starlette">
    <img src="https://badge.fury.io/py/tartiflette-starlette.svg" alt="Package version">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="Code style">
    </a>
</p>

# tartiflette-starlette

ASGI adapter for the [Tartiflette] GraphQL engine, powered by [Starlette].

[tartiflette]: https://tartiflette.io
[starlette]: https://www.starlette.io

The included `TartifletteApp` is an ASGI wrapper with the following features:

- Compatible with any ASGI server and framework.
- Standalone and sub-app serving.
- Built-in [GraphiQL] client.

[graphiql]: https://github.com/graphql/graphiql

**Note**: WebSocket subscriptions aren't supported yet.

**Table of contents**

- [Quickstart](#quickstart)
- [Installation](#installation)
- [User guide](#user-guide)
- [API Reference](#api-reference)
- [FAQ](#faq)

## Quickstart

```python
from tartiflette import Resolver
from tartiflette_starlette import TartifletteApp

@Resolver("Query.hello")
async def hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"

sdl = """
  type Query {
    hello(name: String): String
  }
"""

app = TartifletteApp(sdl=sdl)
```

Save the file as `graphql.py` and start a [uvicorn] server:

[uvicorn]: https://www.uvicorn.org

```bash
uvicorn graphql:app
```

> **Note**: the GraphQL endpoint is exposed on `/` by default.

Make a request:

```bash
curl -H "Content-Type: application/graphql"  -d '{ hello(name: "Chuck") }' http://localhost:8000
```

Response:

```json
{ "data": { "hello": "Hello, Chuck!" }, "errors": null }
```

Or access `http://localhost:8000` in a browser to make interactive queries using the built-in [GraphiQL] client:

![](https://github.com/tartiflette/tartiflette-starlette/raw/master/img/graphiql.png)

## Installation

First [install Tartiflette](https://tartiflette.io/docs/tutorial/install-tartiflette), then run:

```bash
pip install tartiflette-starlette
```

**Note**: `tartiflette-starlette` uses Starlette 0.12+ and requires Python 3.6+.

> ⚠️ This package is still under development. Make sure to pin your dependencies!

## User guide

The `TartifletteApp` class is an ASGI3-compliant application. There are two ways to use it:

- Serve it as a standalone ASGI app.
- Mount it as an endpoint of another ASGI app (e.g. a Starlette application).

### Standalone ASGI app

The [Quickstart](#quickstart) example shows how to build a `TartifletteApp` and serve it as a standalone ASGI app.

The app is served using Uvicorn, but any other ASGI web server will do, for example:

- [uvicorn]
- [hypercorn](https://github.com/pgjones/hypercorn)
- [daphne](https://github.com/django/daphne)

### Submounting on another ASGI app

#### How it works

Most ASGI web frameworks provide a way to **mount** another ASGI app at a given URL prefix. You can use this to serve a `TartifletteApp` at an endpoint such as `/graphql` on the root ASGI application.

This is useful to have **a GraphQL endpoint _and_ other (non-GraphQL) endpoints** within a single application. For example, to have a REST endpoint at `/api/users` and a GraphQL endpoint at `/graphql`.

> **Important**: this should work with _**any**_ web framework that supports ASGI submounting — it doesn't have to be Starlette. See also: [What is the role of Starlette?](#what-is-the-role-of-starlette)

#### Starlette example

```python
from starlette.applications import Starlette
from tartiflette import Resolver
from tartiflette_starlette import TartifletteApp

app = Starlette()

@app.route("/")
async def home(request):
  return PlainTextResponse("Hello, world!")

@Resolver("Query.hello")
async def hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"

sdl = """
  type Query {
    hello(name: String): String
  }
"""

graphql = TartifletteApp(sdl=sdl)
app.mount("/graphql", graphql)
```

Save the file as `app.py`, and serve it with [uvicorn]:

```bash
uvicorn app:app
```

Make a request:

```bash
curl -H "Content-Type: application/graphql"  -d '{ hello(name: "Chuck") }' http://localhost:8000/graphql/
```

Response:

```json
{ "data": { "hello": "Hello, Chuck!" }, "errors": null }
```

### Making requests

`tartiflette-starlette` complies with the [GraphQL spec](https://graphql.org/learn/serving-over-http/#http-methods-headers-and-body), which allows you to pass the query in several ways:

- **URL query string** (methods: `GET`, `POST`):

```bash
curl 'http://localhost:8000?query=\{hello(name:"Chuck")\}'
```

- **JSON-encoded body** (methods: `POST`):

```bash
curl \
  -H "Content-Type: application/json" \
  -d '{"query": "{ hello(name: \"Chuck\") }"}' \
  http://localhost:8000
```

- **Raw body** with the `application/graphql` content type (methods: `POST`):

```bash
curl \
  -H "Content-Type: application/graphql" \
  -d '{ hello(name: "Chuck") }' \
  http://localhost:8000
```

**Note**: you may have your GraphQL API served at a different endpoint.

### Accessing request information

You can access the Starlette `Request` object from resolvers using `context["req"]`:

```python
@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info) -> str:
    request = context["req"]
    return getattr(request.state, "user", "a mystery")
```

See also [Requests](https://www.starlette.io/requests/) in the Starlette documentation.

## API Reference

### `tartiflette_starlette.TartifletteApp`

#### Parameters

**Note**: all parameters are keyword-only.

- `engine (Engine)`: a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl (str)`: a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `graphiql (bool)`: whether to show the GraphiQL client when accessing the endpoint in a web browser. Defaults to `True`.
- `path (str)`: the path which clients should make GraphQL queries to. Defaults to `""`.
- `schema_name (str)`: name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

#### Methods

- `__call__(scope, receive, send)`: implementation of the ASGI3 callable interface.

#### Error responses

| Status code                | Description                                               |
| -------------------------- | --------------------------------------------------------- |
| 400 Bad Request            | The GraphQL query could not be found in the request data. |
| 405 Method Not Allowed     | The HTTP method is not one of `GET`, `HEAD` or `POST`.    |
| 415 Unsupported Media Type | A POST request was made with an unsupported media type.   |

## FAQ

### Does this package ship with Tartiflette?

**No**. You need to install Tartiflette yourself, as described in [Installation](#installation).

### Do I need to learn GraphQL/Tartiflette to use this package?

**Yes**, probably. `tartiflette-starlette` is only an ASGI adapter for Tartiflette, so once you've got the ASGI app up and running, you're in Tartiflette territory.

Here are some resources you may find useful:

- [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/getting-started)
- [Introduction to GraphQL](https://graphql.org/learn/)
- [Tartiflette API reference](https://tartiflette.io/docs/api/engine)

### What is the role of Starlette?

`tartiflette-starlette` uses Starlette as an **ASGI toolkit**. More specifically, it uses its request and response classes.

This is **fully transparent** from a user perspective. If you're [submounting your GraphQL app](#submounting-on-another-asgi-app), your web framework you use doesn't need to be built on top of Starlette — it just needs to speak ASGI.

### What is ASGI?

ASGI provides a standard interface between async-capable Python web servers, frameworks, and applications.

See also the [ASGI documentation](https://asgi.readthedocs.io/en/latest/).

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-starlette/tree/master/CONTRIBUTING.md).

## Changelog

Changes to this project are recorded in the [changelog](https://github.com/tartiflette/tartiflette-starlette/tree/master/CHANGELOG.md).

## License

MIT
