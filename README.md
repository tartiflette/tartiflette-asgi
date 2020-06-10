<div align="center">
  <img src="https://raw.githubusercontent.com/tartiflette/tartiflette-asgi/master/img/tartiflette-asgi.png" alt="tartiflette-asgi logo"/>
</div>

<p align="center">
  <a href="https://github.com/tartiflette/tartiflette-asgi/actions">
    <img src="https://github.com/tartiflette/tartiflette-asgi/workflows/Build/badge.svg?branch=master" alt="Build status">
  </a>
  <a href="https://pypi.org/project/tartiflette-asgi">
    <img src="https://badge.fury.io/py/tartiflette-asgi.svg" alt="Package version">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code_style-black-000000.svg" alt="Code style">
    </a>
</p>

`tartiflette-asgi` is a wrapper that provides ASGI support for the [Tartiflette](https://tartiflette.io) Python GraphQL engine.

It is ideal for serving a GraphQL API over HTTP, or adding a GraphQL API endpoint to an existing ASGI application (e.g. FastAPI, Starlette, Quart, etc).

Full documentation is available at: https://tartiflette.github.io/tartiflette-asgi

## Requirements

`tartiflette-asgi` is compatible with:

- Python 3.6, 3.7 or 3.8.
- Tartiflette 1.x.

## Quickstart

First, install Tartiflette's external dependencies, as explained in the [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/install-tartiflette).

Then, you can install Tartiflette and `tartiflette-asgi` using `pip`:

```bash
pip install tartiflette "tartiflette-asgi==0.*"
```

You'll also need an [ASGI web server](https://github.com/florimondmanca/awesome-asgi#servers). We'll use [Uvicorn](http://www.uvicorn.org/) here:

```bash
pip install uvicorn
```

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
{ "data": { "hello": "Hello, Chuck!" } }
```

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/tartiflette/tartiflette-asgi/tree/master/CONTRIBUTING.md).

## Changelog

Changes to this project are recorded in the [changelog](https://github.com/tartiflette/tartiflette-asgi/tree/master/CHANGELOG.md).

## License

MIT
