# tartiflette-starlette

[ASGI] adapter for the [Tartiflette] asynchronous GraphQL engine powered by [Starlette].

**Note**: although it relies on Starlette for HTTP request processing, **`tartiflette-starlette` can be used with any ASGI web framework** that supports mounting ASGI sub-applications.

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

The `Tartiflette` app provided by `tartiflette-starlette` is an ASGI3-compliant application.

As an example, let's a GraphQL endpoint to a Starlette application by mounting a `Tartiflette` instance at `/graphql`:

```python
# main.py
from starlette.applications import Starlette
from tartiflette import Resolver

from tartiflette_starlette import Tartiflette


@Resolver("Query.hello")
async def resolve_hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!"


sdl = """
    type Query {
        hello(name: String): String
    }
"""

app = Starlette()
app.add_route("/graphql", Tartiflette(sdl=sdl))
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

![](https://github.com/florimondmanca/tartiflette-starlette/blob/master/img/graphiql.png)

It's just Tartiflette from there! Learn more by reading the [Tartiflette documentation][tartiflette].

## API Reference

### `tartiflette_starlette.Tartiflette`

**Note**: all parameters are keyword-only.

- `engine (Engine)`: a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl (str)`: a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `graphiql (bool)`: whether to serve the GraphiQL when accessing the endpoint via a web browser. Defaults to `True`.
- `schema_name (str)`: name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

## Contributing

Want to contribute? Awesome! Be sure to read our [Contributing guidelines](https://github.com/florimondmanca/tartiflette-starlette/blob/master/CONTRIBUTING.md).

## License

MIT
