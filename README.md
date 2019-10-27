<div align="center">
  <img src="https://user-images.githubusercontent.com/158689/58954519-b05ad680-8799-11e9-9134-90622e7731f3.png" alt="tartiflette-asgi logo"/>
</div>

<p align="center">
  <a href="https://travis-ci.org/tartiflette/tartiflette-asgi">
    <img src="https://travis-ci.org/tartiflette/tartiflette-asgi.svg?branch=master" alt="Build status">
  </a>
  <a href="https://pypi.org/project/tartiflette-asgi">
    <img src="https://badge.fury.io/py/tartiflette-asgi.svg" alt="Package version">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="Code style">
    </a>
</p>

`tartiflette-asgi` (previously `tartiflette-starlette`) is a wrapper that provides ASGI support for the [Tartiflette] Python GraphQL engine.

[tartiflette]: https://tartiflette.io

Build your GraphQL API with Tartiflette, then use the included `TartifletteApp` and get the following:

- Compatibility with any ASGI server and framework.
- Standalone and sub-app serving.
- Built-in [GraphiQL] client.
- Support for [GraphQL subscriptions over WebSocket](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md).

[graphiql]: https://github.com/graphql/graphiql

---

**Note**: `tartiflette-asgi >= 0.7` (and `tartiflette-starlette == 0.6.*`) is only compatible with Tartiflette 1.x. For compatibility with Tartiflette 0.x, please install `tartiflette-starlette == 0.5.*`.

---

**Table of contents**

- [Quickstart](#quickstart)
- [Installation](#installation)
- [User guide](#user-guide)
  - [Standalone serving](#standalone-serving)
  - [ASGI submounting](#asgi-submounting)
  - [Making requests](#making-requests)
  - [Accessing request information](#accessing-request-information)
  - [GraphiQL client](#graphiql-client)
  - [WebSocket subscriptions (Advanced)](#websocket-subscriptions-advanced)
- [API Reference](#api-reference)
- [FAQ](#faq)

## Quickstart

```python
from tartiflette import Resolver
from tartiflette_asgi import TartifletteApp

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

![](https://github.com/tartiflette/tartiflette-asgi/raw/master/img/graphiql.png)

## Installation

1. Install Tartiflette's external dependencies as explained in the [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/install-tartiflette).
2. Install `tartiflette-asgi` from PyPI:

```bash
pip install "tartiflette-asgi==0.*"
```

This will also install [Tartiflette] and [Starlette], so you're good to go!

[starlette]: https://www.starlette.io

**Note**: `tartiflette-asgi` requires Python 3.6+.

## User guide

The [`TartifletteApp`](#tartifletteapp) class is an ASGI3-compliant application. There are two ways to use it:

- Serve it as a standalone ASGI app.
- Mount it as an endpoint of another ASGI app (e.g. a Starlette application).

### Standalone serving

The [Quickstart](#quickstart) example shows how to build a `TartifletteApp` and serve it as a standalone ASGI app.

The app is served using Uvicorn, but any other ASGI web server will do, for example:

- [uvicorn]
- [hypercorn](https://github.com/pgjones/hypercorn)
- [daphne](https://github.com/django/daphne)

### ASGI submounting

Most ASGI web frameworks provide a way to **mount** another ASGI app at a given URL prefix. You can use this to serve a `TartifletteApp` at an endpoint such as `/graphql` on the root ASGI application.

This is useful to have **a GraphQL endpoint _and_ other (non-GraphQL) endpoints** within a single application. For example, to have a REST endpoint at `/api/users` and a GraphQL endpoint at `/graphql`.

> **Important**: this should work with _**any**_ web framework that supports ASGI submounting — it doesn't have to be Starlette. See also: [What is the role of Starlette?](#what-is-the-role-of-starlette)

#### Starlette example

```python
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from tartiflette import Resolver
from tartiflette_asgi import TartifletteApp, mount

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
mount.starlette(app, "/graphql", graphql)  # (*)
```

> (\*) This is a shorthand for:
>
> ```python
> app.mount("/graphql", graphql)
> app.add_event_handler("startup", graphql.startup)
> ```

Save the file as `app.py`, and serve it with [uvicorn]:

```bash
uvicorn app:app
```

Make a request:

```bash
curl -H "Content-Type: application/graphql/"  -d '{ hello(name: "Chuck") }' http://localhost:8000
```

> **Note**: if you receive a `307 Temporary Redirect` response, make sure to include the trailing slash: `/graphql/`.

Response:

```json
{ "data": { "hello": "Hello, Chuck!" } }
```

#### General approach

Assuming you have an instance of `TartifletteApp` called `graphql`, you need to:

1. Add the `graphql` app as a sub-application (also known as "mounting"). The parent ASGI application may expose a method such as `.mount()` for this purpose.
2. Add `graphql.startup` as a startup event handler so that the Tartiflette engine is built upon application startup. Note that:

- Not doing this will result in a `RuntimeError` when requesting the GraphQL endpoint.
- The parent ASGI application may expose a method such as `.add_event_handler()` for this purpose.
- This is only required if the parent ASGI application does not call lifespan event handlers for sub-applications, as is the case for Starlette.

**Tip**: the [`mount`](#mount) module provides mounting helpers for various ASGI frameworks.

### Making requests

`tartiflette-asgi` complies with the [GraphQL spec](https://graphql.org/learn/serving-over-http/#http-methods-headers-and-body), which allows you to pass the query in several ways:

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

### GraphiQL client

By default, the GraphQL endpoint provided by `TartifletteApp` serves a [GraphiQL] client when it is accessed from a web browser. It can be customized using the `GraphiQL` helper.

Here's an example:

```python
from tartiflette_asgi import TartifletteApp, GraphiQL

app = TartifletteApp(
    sdl="""
    type Query {
        hello(name: String): String
    }
    """,
    graphiql=GraphiQL(
        path="/graphiql",
        default_headers={"Authorization": "Bearer 123"},
        default_variables={"name": "world"},
        default_query="""
        query Hello($name: String) {
            hello(name: $name)
        }
        """,
    ),
)
```

Save this as `graphql.py` and run `uvicorn graphql:app`. You should see the customized GraphiQL client when accessing http://127.0.0.1/graphiql:

![](https://github.com/tartiflette/tartiflette-asgi/raw/master/img/graphiql-custom.png)

See [`GraphiQL`](#graphiql) in the API reference for a complete description of the available options.

### Providing additional context to resolvers

You can inject your own services, functions or data into the GraphQL `context` using the `context` option.

For example, assuming you use a publish/subscribe library named `pubsub`, you could write:

```python
from pubsub import PubSub  # Fake

@Resolver("Query.human")
async def resolve_human(parent, args, context, info):
    pubsub = context["pubsub"]
    # ...
    await pubsub.publish("human_fetched", args)

graphql = TartifletteApp(
  # ...,
  context={"pubsub": PubSub()},
)
```

### WebSocket subscriptions (Advanced)

This package provides support for [GraphQL subscriptions](https://graphql.org/blog/subscriptions-in-graphql-and-relay/) over WebSocket. Subscription queries can be issued via the built-in GraphiQL client, as well as [Apollo GraphQL](https://www.apollographql.com/docs/react/advanced/subscriptions/) and any other client that uses the [subscriptions-transport-ws](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md) protocol.

Example:

```python
import asyncio
from tartiflette import Subscription
from tartiflette_asgi import TartifletteApp, GraphiQL

sdl = """
type Query {
  _: Boolean
}

type Subscription {
  timer(seconds: Int!): Timer
}

enum Status {
  RUNNING
  DONE
}

type Timer {
  remainingTime: Int!
  status: Status!
}
"""

@Subscription("Subscription.timer")
async def on_timer(parent, args, context, info):
    seconds = args["seconds"]
    for i in range(seconds):
        yield {"timer": {"remainingTime": seconds - i, "status": "RUNNING"}}
        await asyncio.sleep(1)
    yield {"timer": {"remainingTime": 0, "status": "DONE"}}

app = TartifletteApp(
    sdl=sdl,
    subscriptions=True,
    graphiql=GraphiQL(
        default_query="""
        subscription {
          timer(seconds: 5) {
            remainingTime
            status
          }
        }
        """
    ),
)
```

> **Note**: the subscriptions endpoint is exposed on `/subscriptions` by default.

Save this file as `graphql.py`, then run `$ uvicorn graphql:app`. Open the GraphiQL client at http://localhost:8000, and hit "Play"! The timer should update on real-time.

![](https://github.com/tartiflette/tartiflette-asgi/raw/master/img/graphiql-subscriptions.png)

See [`Subscriptions`](#subscriptions) in the API reference for a complete description of the available options.

For more information on using subscriptions in Tartiflette, see the [Tartiflette documentation](https://tartiflette.io/docs/api/subscription).

## API Reference

> **Note**: unless specified, components documented here can be imported from `tartiflette_asgi` directly, e.g. `from tartiflette_asgi import TartifletteApp`.

### `TartifletteApp`

#### Parameters

**Note**: all parameters are keyword-only.

- `engine` (`Engine`): a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl` (`str`): a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `path` (`str`, optional): the path which clients should make GraphQL queries to. Defaults to `"/"`.
- `graphiql` (`GraphiQL` or `bool`, optional): configuration for the GraphiQL client. Defaults to `True`, which is equivalent to `GraphiQL()`. Use `False` to not register the GraphiQL client.
- `subscriptions` (`Subscriptions` or `bool`, optional): subscriptions configuration. Defaults to `True`, which is equivalent to `Subscriptions(path="/subscriptions")`. Leave empty or pass `None` to not register the subscription WebSocket endpoint.
- `context` (`dict`, optional): a copy of this dictionary is passed to resolvers when executing a query. Defaults to `{}`. Note: the Starlette `Request` object is always present as `req`.
- `schema_name` (`str`, optional): name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

#### Methods

- `__call__(scope, receive, send)`: ASGI3 implementation.

#### Error responses

| Status code                | Description                                                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 400 Bad Request            | The GraphQL query could not be found in the request data.                                                                        |
| 404 Not Found              | The request does not match the GraphQL or GraphiQL endpoint paths.                                                               |
| 405 Method Not Allowed     | The HTTP method is not one of `GET`, `HEAD` or `POST`.                                                                           |
| 415 Unsupported Media Type | The POST request made to the GraphQL endpoint uses a `Content-Type` different from `application/json` and `application/graphql`. |

### `GraphiQL`

Configuration helper for the GraphiQL client.

#### Parameters

**Note**: all parameters are keyword-only.

- `path` (`str`, optional): the path of the GraphiQL endpoint, **relative to the root path which `TartifletteApp` is served at**. If not given, defaults to the `path` given to `TartifletteApp`.
- `default_headers` (`dict`, optional): extra HTTP headers to send when calling the GraphQL endpoint.
- `default_query` (`str`, optional): the default query to display when accessing the GraphiQL interface.
- `default_variables` (`dict`, optional): default [variables][graphql-variables] to display when accessing the GraphiQL interface.
- `template` (`str`, optional): an HTML template to use instead of the default one. In the template, `default_headers`, `default_query` and `default_variables`, as well as the GraphQL `endpoint`, are available as strings (JSON-encoded if needed) using template string substitutions, e.g.:

```js
const endpoint = `${endpoint}`; // This is where the API call should be made.
const defaultHeaders = JSON.parse(`${default_headers}`);
```

[graphql-variables]: https://graphql.org/learn/queries/#variables

### `Subscriptions`

Configuration helper for WebSocket subscriptions.

#### Parameters

**Note**: all parameters are keyword-only.

- `path` (`str`): the path of the subscriptions WebSocket endpoint, **relative to the root path which `TartifletteApp` is served at**. If not given, defaults to `/subscriptions`.

### `mount`

This module contains helpers for mounting a `TartifletteApp` on other ASGI applications. Use these helpers to make sure you comply with the steps described in [General approach](#general-approach).

#### Parameters

All mounting helpers expect the same parameters:

- `parent` (ASGI app): the parent ASGI application which the `TartifletteApp` must be mounted onto.
- `path` (`str`): the URL path where the `TartifletteApp` should be mounted.
- `app` (`TartifletteApp`): the `TartifletteApp` to mount.
- `**kwargs` (any): extra keyword arguments passed to the mount implementation of the `parent` app.

#### Available helpers

| Helper              | Mount implementation | Startup event handler implementation |
| ------------------- | -------------------- | ------------------------------------ |
| `mount.starlette()` | `parent.mount()`     | `parent.add_event_handler()`         |

> Missing a helper for your favorite framework? Feel free to [open a pull request](https://github.com/tartiflette/tartiflette-asgi/compare)!

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

`tartiflette-asgi` uses Starlette as a lightweight ASGI toolkit: internally, it uses Starlette's request and response classes, and some other components.

Luckily, this does not require your applications to use Starlette at all.

For example, if you are [submounting your GraphQL app](#submounting-on-another-asgi-app) on an app built with an async web framework, this framework does not need to use Starlette — it just needs to speak ASGI.

### What is ASGI?

ASGI provides a standard interface between async-capable Python web servers, frameworks, and applications.

See also the [ASGI documentation](https://asgi.readthedocs.io/en/latest/).

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-asgi/tree/master/CONTRIBUTING.md).

## Changelog

Changes to this project are recorded in the [changelog](https://github.com/tartiflette/tartiflette-asgi/tree/master/CHANGELOG.md).

## License

MIT
