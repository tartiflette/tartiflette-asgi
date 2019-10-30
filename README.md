<div align="center">
  <img src="https://raw.githubusercontent.com/tartiflette/tartiflette-asgi/master/img/tartiflette-asgi.png" alt="tartiflette-asgi logo"/>
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

`tartiflette-asgi` (previously `tartiflette-starlette`) is a wrapper that provides ASGI support for the [Tartiflette] Python GraphQL engine. It is ideal for serving a GraphQL API over HTTP, or adding a GraphQL API endpoint to an existing ASGI application.

[tartiflette]: https://tartiflette.io

Build a GraphQL API using Tartiflette, then use `tartiflette-asgi` to achieve the following:

- Serve your GraphQL API as a standalone ASGI application using an ASGI server (e.g. Uvicorn, Daphne or Hypercorn).
- Mount your GraphQL API endpoint onto an existing ASGI application (built using e.g. Starlette, FastAPI, Responder, Quart or Sanic).
- Make interactive queries using the built-in GraphiQL client.
- Implement GraphQL subscriptions thanks to built-in support for the [GraphQL subscriptions over WebSocket protocol](https://github.com/apollographql/subscriptions-transport-ws/blob/master/PROTOCOL.md).

**Table of contents**

- [Requirements](#requirements)
- [Quickstart](#quickstart)
  - [Installation](#installation)
  - [Example](#example)
- [Usage](#usage)
  - [Making requests](#making-requests)
  - [Accessing request information](#accessing-request-information)
  - [Shared GraphQL context](#shared-graphql-context)
  - [GraphiQL client](#graphiql-client)
  - [WebSocket subscriptions (Advanced)](#websocket-subscriptions-advanced)
- [ASGI sub-mounting](#asgi-sub-mounting)
- [API Reference](#api-reference)
- [FAQ](#faq)

## Requirements

`tartiflette-asgi` is compatible with:

- Python 3.6, 3.7 or 3.8.
- Tartiflette 1.x.

## Quickstart

### Installation

First, install Tartiflette's external dependencies, as explained in the [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/install-tartiflette).

Then, you can install Tartiflette and `tartiflette-asgi` using `pip`:

```bash
pip install tartiflette "tartiflette-asgi==0.*"
```

You'll also need an [ASGI web server](https://github.com/florimondmanca/awesome-asgi#servers). For example, let's install [Uvicorn](http://www.uvicorn.org/):

```bash
pip install uvicorn
```

### Example

Create an application that exposes a `TartifletteApp` instance:

```python
from tartiflette import Resolver
from tartiflette_asgi import TartifletteApp

@Resolver("Query.hello")
async def hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"

sdl = "type Query { hello(name: String): String }"
app = TartifletteApp(sdl=sdl, path="/graphql")
```

Save this file as `graphql.py`, then start the server:

```bash
uvicorn graphql:app
```

Make an HTTP request containing a GraphQL query:

```bash
curl http://localhost:8000/graphql -d '{ hello(name: "Chuck") }' -H "Content-Type: application/graphql"
```

You should get the following JSON response:

```json
{"data": {"hello": "Hello, Chuck!"}}
```

## Usage

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

All the information about the current HTTP request (URL, headers, query parameters, etc) is available on `context["req"]`, which returns a Starlette `Request` object representing the current HTTP request.

```python
@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info) -> str:
    request = context["req"]
    who = request.query_params.get("username", "unknown")
    return who
```

For detailed usage notes about the `Request` object, see [Requests](https://www.starlette.io/requests/) in the Starlette documentation.

## Shared GraphQL context

If you need to make services, functions or data available to GraphQL resolvers, you can use `TartifletteApp(context=...)`. Contents of the `context` argument will be merged into the GraphQL `context` passed to resolvers.

For example:

```python
import os
from tartiflette import Resolver
from tartiflette_asgi import TartifletteApp

@Resolver("Query.human")
async def resolve_human(parent, args, context, info):
    planet = context["planet"]
    return f"Human living on {planet}"

app = TartifletteApp(
  sdl="type Query { human(): String }",
  context={"planet": os.getenv("PLANET", "Earth")},
)
```

### GraphiQL client

#### Default behavior

When you access the GraphQL endpoint in a web browser, `TartifletteApp` serves a [GraphiQL](https://github.com/graphql/graphiql) client, which allows you to make interactive GraphQL queries in the browser.

![](https://github.com/tartiflette/tartiflette-asgi/raw/master/img/graphiql.png)

#### Customization

You can customize the GraphiQL interface using `TartifletteApp(graphiql=GraphiQL(...))`.

For example, this snippet will:

- Serve the GraphiQL web interface at `/graphiql`.
- Send an `Authorization` header when making requests to the API endpoint.
- Setup the default variables and query to show when accessing the web interface for the first time.

```python
from tartiflette_asgi import TartifletteApp, GraphiQL

sdl = "type Query { hello(name: String): String }"

graphiql = GraphiQL(
    path="/graphiql",
    default_headers={"Authorization": "Bearer 123"},
    default_variables={"name": "world"},
    default_query="""
    query Hello($name: String) {
        hello(name: $name)
    }
    """,
)

app = TartifletteApp(sdl=sdl, graphiql=graphiql)
```

If you run this application, you should see the customized GraphiQL client when accessing http://localhost:8000/graphiql:

![](https://raw.githubusercontent.com/tartiflette/tartiflette-asgi/master/img/graphiql-custom.png)

For the full list of options, see [`GraphiQL`](#graphiql).

#### Disabling the GraphiQL client

To disable the GraphiQL client altogether, use `TartifletteApp(graphiql=False)`.

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

## ASGI sub-mounting

You can mount a `TartifletteApp` instance as a sub-route of another ASGI application.

This is useful to have a GraphQL endpoint _and_ other (non-GraphQL) endpoints within a single application. For example, you may wnat to have a REST endpoint at `/api/users`, or serve an HTML page at `/index.html`, as well as expose a GraphQL endpoint at `/graphql`.

How to achieve this depends on the specific ASGI web framework you are using, so this page documents how to achieve it in various situations.

### General approach

In general, you'll need to do the following:

1. Create a `TartifletteApp` application instance.
1. Mount it under the main ASGI application's router. (Most ASGI frameworks expose a method such as `.mount()` for this purpose.)
1. Register the startup lifespan event handler on the main ASGI application. (Frameworks typically expose a method such as `.add_event_handler()` for this purpose.)

> **Important**
>
> The startup event handler is responsible for preparing the GraphQL engine (a.k.a. [cooking the engine](https://tartiflette.io/docs/api/engine#cook-your-tartiflette)), e.g. loading modules, SDL files, etc.
>
> If your ASGI framework does not implement the lifespan protocol and/or does not allow to register custom lifespan event handlers, or if you're working at the raw ASGI level, you can still use `tartiflette-asgi` but you'll need to add lifespan support yourself, e.g. using [asgi-lifespan](https://github.com/florimondmanca/asgi-lifespan).

### Examples

This section documents how to mount a `TartifletteApp` instance under an ASGI application for various ASGI web frameworks.

To run an example:

- Save the application script as `graphql.py`.
- Run the server using `$ uvicorn graphql:app`.
- Make a request using:

```bash
curl http://localhost:8000/graphql -d '{ hello(name: "Chuck") }' -H "Content-Type: application/graphql"
```

#### Starlette

```python
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from tartiflette import Resolver
from tartiflette_asgi import TartifletteApp

# Create a Starlette application.

app = Starlette()

# Maybe add some non-GraphQL routes...

@app.route("/")
async def home(request):
  return PlainTextResponse("Hello, world!")

# Create a 'TartifletteApp' instance.

@Resolver("Query.hello")
async def hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"

sdl = "type Query { hello(name: String): String }"
graphql = TartifletteApp(sdl=sdl)

# Mount it under the Starlette application.

app.mount("/graphql", graphql)
app.add_event_handler("startup", graphql.startup)
```

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
