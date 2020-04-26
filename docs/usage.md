# User Guide

## Creating an application

The main piece of API that `tartiflette-asgi` brings is `TartifletteApp`, an ASGI3-compliant ASGI application.

You can build it from either:

- The Schema Definition Language (SDL):

```python
# This is an SDL string, but Tartiflette supports
# other formats, e.g. paths to schema files or directories.
sdl = "type Query { hello: String }"

app = TartifletteApp(sdl=sdl)
```

- A Tartiflette `Engine` instance:

```python
from tartiflette import Engine

engine = Engine(sdl=..., modules=[...])
app = TartifletteApp(engine=engine)
```

For more information on what values `sdl` and `engine` can accept, see the [Engine API reference](https://tartiflette.io/docs/api/engine).

## Routing

You can define which URL path the `TartifletteApp` should be accessible at using the `path` parameter.

It is served at `/` by default, but a popular choice is to serve it at `/graphql`:

```python
app = TartifletteApp(..., path="/graphql")
```

## Making requests

`tartiflette-asgi` allows you to pass the query in several ways:

- URL query string (methods: `GET`, `POST`):

```bash
curl 'http://localhost:8000/graphql?query=\{hello(name:"Chuck")\}'
```

- JSON-encoded body (methods: `POST`):

```bash
curl http://localhost:8000/graphql \
  -d '{"query": "{ hello(name: \"Chuck\") }"}' \
  -H "Content-Type: application/json"
```

- Raw body with the `application/graphql` content type (methods: `POST`):

```bash
curl http://localhost:8000/graphql \
  -d '{ hello(name: "Chuck") }' \
  -H "Content-Type: application/graphql"
```

## GraphiQL client

### Default behavior

When you access the GraphQL endpoint in a web browser, `TartifletteApp` serves a [GraphiQL](https://github.com/graphql/graphiql) client, which allows you to make interactive GraphQL queries in the browser.

![](https://github.com/tartiflette/tartiflette-asgi/raw/master/img/graphiql.png)

### Customization

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

If you run this application, you should see the customized GraphiQL client when accessing [http://localhost:8000/graphiql](http://localhost:8000/graphiql):

![](https://raw.githubusercontent.com/tartiflette/tartiflette-asgi/master/img/graphiql-custom.png)

For the full list of options, see [`GraphiQL`](/api/#graphiql).

### Disabling the GraphiQL client

To disable the GraphiQL client altogether, use `TartifletteApp(graphiql=False)`.

## ASGI sub-mounting

You can mount a `TartifletteApp` instance as a sub-route of another ASGI application.

This is useful to have a GraphQL endpoint _and_ other (non-GraphQL) endpoints within a single application. For example, you may want to have a REST endpoint at `/api/users`, or serve an HTML page at `/index.html`, as well as expose a GraphQL endpoint at `/graphql`.

How to achieve this depends on the specific ASGI web framework you are using, so this section documents how to achieve it in various situations.

### General approach

In general, you'll need to do the following:

1. Create a `TartifletteApp` application instance.
1. Mount it under the main ASGI application's router. (Most ASGI frameworks expose a method such as `.mount()` for this purpose.)
1. Register the startup lifespan event handler on the main ASGI application. (Frameworks typically expose a method such as `.add_event_handler()` for this purpose.)

!!! important
The startup event handler is responsible for preparing the GraphQL engine (a.k.a. [cooking the engine](https://tartiflette.io/docs/api/engine#cook-your-tartiflette)), e.g. loading modules, SDL files, etc.

    If your ASGI framework does not implement the lifespan protocol and/or does not allow to register custom lifespan event handlers, or if you're working at the raw ASGI level, you can still use `tartiflette-asgi` but you'll need to add lifespan support yourself, e.g. using [asgi-lifespan](https://github.com/florimondmanca/asgi-lifespan).

### Routing

Although `TartifletteApp` has minimal support for [routing](#routing), when using ASGI sub-mounting you'll probably want to leave the `path` parameter on `TartifletteApp` empty, e.g. use:

```python
graphql = TartifletteApp(sdl=...)
app.mount("/graphql", app=graphql)
```

This is because `path` is relative to the mount path on the host ASGI application. As a result, mounting at `/graphql` while setting `path="/graphql"` would make the GraphQL API accessible at `/graphql/graphql`, which is typically not what you want.

If you want to have your GraphQL API accessible at `/graphql`, you should do as above, i.e.:

- Leave `path` empty on `TartifletteApp`.
- Mount it at `/graphql` on the host ASGI app.

(Mounting at `/` and setting `path="/graphql"` typically won't have the behavior you'd expect. For example, Starlette would send all requests to your GraphQL endpoint, regardless of whether the requested URL path.)

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
from starlette.routing import Mount, Route
from tartiflette import Resolver
from tartiflette_asgi import TartifletteApp


# Create a 'TartifletteApp' instance.

@Resolver("Query.hello")
async def hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"

sdl = "type Query { hello(name: String): String }"
graphql = TartifletteApp(sdl=sdl)

# Declare regular routes as seems fit...

async def home(request):
  return PlainTextResponse("Hello, world!")

# Create a Starlette application, mounting the 'TartifletteApp' instance.

routes = [
    Route("/", endpoint=home),
    Mount("/graphql", graphql),
]
app = Starlette(routes=routes, on_startup=graphql.startup)
```

## Advanced usage

### Accessing request information

All the information about the current HTTP request (URL, headers, query parameters, etc) is available on `context["req"]`, which returns a Starlette `Request` object representing the current HTTP request.

```python
@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info):
    request = context["req"]
    who = request.query_params.get("username", "unknown")
    return who
```

For detailed usage notes about the `Request` object, see [Requests](https://www.starlette.io/requests/) in the Starlette documentation.

### Shared GraphQL context

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

### WebSocket subscriptions

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

See [`Subscriptions`](/api/#subscriptions) in the API reference for a complete description of the available options.

For more information on using subscriptions in Tartiflette, see the [Tartiflette documentation](https://tartiflette.io/docs/api/subscription).
