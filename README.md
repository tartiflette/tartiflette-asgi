<div align="center">
  <img src="https://user-images.githubusercontent.com/158689/58954519-b05ad680-8799-11e9-9134-90622e7731f3.png" alt="tartiflette-starlette logo"/>
</div>

<p align="center">
  <a href="https://travis-ci.org/tartiflette/tartiflette-starlette">
    <img src="https://travis-ci.org/tartiflette/tartiflette-starlette.svg?branch=master" alt="Build status">
  </a>
  <a href="https://pypi.org/project/tartiflette-starlette">
    <img src="https://badge.fury.io/py/tartiflette-starlette.svg" alt="Package version">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="Code style">
    </a>
</p>

`tartiflette-starlette` is a wrapper that provides ASGI support for the [Tartiflette] Python GraphQL engine.

[tartiflette]: https://tartiflette.io

Build your GraphQL API with Tartiflette, then use the included `TartifletteApp` and get the following:

- Compatibility with any ASGI server and framework.
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
{ "data": { "hello": "Hello, Chuck!" } }
```

Or access `http://localhost:8000` in a browser to make interactive queries using the built-in [GraphiQL] client:

![](https://github.com/tartiflette/tartiflette-starlette/raw/master/img/graphiql.png)

## Installation

1. Install Tartiflette's external dependencies as explained in the [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/install-tartiflette).
2. Install `tartiflette-starlette` from PyPI:

```bash
pip install tartiflette-starlette
```

This will also install [Tartiflette] and [Starlette], so you're good to go!

[starlette]: https://www.starlette.io

**Note**: `tartiflette-starlette` requires Python 3.6+.

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
from starlette.responses import PlainTextResponse
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
curl -H "Content-Type: application/graphql"  -d '{ hello(name: "Chuck") }' http://localhost:8000
```

Response:

```json
{ "data": { "hello": "Hello, Chuck!" } }
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

> **Note**: unless specified, components documented here can be imported from `tartiflette_starlette` directly, e.g. `from tartiflette_starlette import TartifletteApp`.

### `TartifletteApp`

#### Parameters

**Note**: all parameters are keyword-only.

- `engine` (`Engine`): a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl` (`str`): a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `graphiql` (`GraphiQL` or `bool`, optional): configuration for the GraphiQL client. Defaults to `True`, which is equivalent to `GraphiQL()`. Use `False` to not register the GraphiQL client.
- `path` (`str`, optional): the path which clients should make GraphQL queries to. Defaults to `"/"`.
- `schema_name` (`str`, optional): name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

#### Methods

- `__call__(scope, receive, send)`: ASGI3 implementation.

### `GraphiQL`

Configuration helper for the GraphiQL client.

#### Parameters

**Note**: all parameters are keyword-only.

- `path` (`str`, optional): the path of the GraphiQL endpoint. Defaults to the `path` given to `TartifletteApp`.
- `template` (`str`, optional): an HTML template to use instead of the default one. In the template, an HTTP request should be made to the GraphQL endpoint (its path is available as `${path}`).

#### Error responses

| Status code                | Description                                                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 400 Bad Request            | The GraphQL query could not be found in the request data.                                                                        |
| 404 Not Found              | The request does not match the GraphQL or GraphiQL endpoint paths.                                                               |
| 405 Method Not Allowed     | The HTTP method is not one of `GET`, `HEAD` or `POST`.                                                                           |
| 415 Unsupported Media Type | The POST request made to the GraphQL endpoint uses a `Content-Type` different from `application/json` and `application/graphql`. |

## FAQ

### Does this package ship with Tartiflette?

**Yes**. Everything is included, which allows you to start building your GraphQL API right away. See also [Installation](#installation).

### Do I need to learn GraphQL/Tartiflette to use this package?

**Yes**: once you've got the `TartifletteApp` ASGI app up and running, you're in Tartiflette territory.

Here are some resources to get you started:

- [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/getting-started)
- [Introduction to GraphQL](https://graphql.org/learn/)
- [Tartiflette API reference](https://tartiflette.io/docs/api/engine)

### What is the role of Starlette?

`tartiflette-starlette` uses Starlette as a lightweight ASGI toolkit: internally, it uses Starlette's request and response classes.

Luckily, this does not require your applications to use Starlette at all.

For example, if you're [submounting your GraphQL app](#submounting-on-another-asgi-app) on an app built with an async web framework, the framework doesn't need to use Starlette — it just needs to speak ASGI.

### What is ASGI?

ASGI provides a standard interface between async-capable Python web servers, frameworks, and applications.

See also the [ASGI documentation](https://asgi.readthedocs.io/en/latest/).

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-starlette/tree/master/CONTRIBUTING.md).

## Changelog

Changes to this project are recorded in the [changelog](https://github.com/tartiflette/tartiflette-starlette/tree/master/CHANGELOG.md).

## License

MIT
