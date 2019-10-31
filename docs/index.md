<div align="center">
  <img src="https://raw.githubusercontent.com/tartiflette/tartiflette-asgi/master/img/tartiflette-asgi.png" alt="tartiflette-asgi logo"/>
</div>

# Introduction

`tartiflette-asgi` (previously `tartiflette-starlette`) is a wrapper that provides ASGI support for the [Tartiflette] Python GraphQL engine.

It is ideal for serving a GraphQL API over HTTP, or adding a GraphQL API endpoint to an existing ASGI application.

[tartiflette]: https://tartiflette.io

Build a GraphQL API using Tartiflette, then use `tartiflette-asgi` to achieve the following:

- Serve your GraphQL API as a standalone ASGI application using an ASGI server (e.g. Uvicorn, Daphne or Hypercorn).
- Mount your GraphQL API endpoint onto an existing ASGI application (built using e.g. Starlette, FastAPI, Responder, Quart or Sanic).
- Make interactive queries using the built-in GraphiQL client.
- Implement real-time querying thanks to GraphQL subscriptions over WebSocket.

## Requirements

`tartiflette-asgi` is compatible with:

- Python 3.6, 3.7 or 3.8.
- Tartiflette 1.x.

## Installation

First, install Tartiflette's external dependencies, as explained in the [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/install-tartiflette).

Then, you can install Tartiflette and `tartiflette-asgi` using `pip`:

```bash
pip install tartiflette "tartiflette-asgi==0.*"
```

You'll also need an [ASGI web server](https://github.com/florimondmanca/awesome-asgi#servers). We'll use [Uvicorn](http://www.uvicorn.org/) throughout this documentation:

```bash
pip install uvicorn
```

## Quickstart

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
