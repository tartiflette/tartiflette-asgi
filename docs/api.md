# API Reference

!!! note
    Unless specified otherwise, components documented here can be imported from `tartiflette_asgi` directly, e.g. `from tartiflette_asgi import TartifletteApp`.

## `TartifletteApp`

### Parameters

**Note**: all parameters are keyword-only.

- `engine` (`Engine`): a Tartiflette [engine](https://tartiflette.io/docs/api/engine). Required if `sdl` is not given.
- `sdl` (`str`): a GraphQL schema defined using the [GraphQL Schema Definition Language](https://graphql.org/learn/schema/). Required if `engine` is not given.
- `path` (`str`, optional): the path which clients should make GraphQL queries to. Defaults to `"/"`.
- `graphiql` (`GraphiQL` or `bool`, optional): configuration for the GraphiQL client. Defaults to `True`, which is equivalent to `GraphiQL()`. Use `False` to not register the GraphiQL client.
- `subscriptions` (`Subscriptions` or `bool`, optional): subscriptions configuration. Defaults to `True`, which is equivalent to `Subscriptions(path="/subscriptions")`. Leave empty or pass `None` to not register the subscription WebSocket endpoint.
- `context` (`dict`, optional): a copy of this dictionary is passed to resolvers when executing a query. Defaults to `{}`. Note: the Starlette `Request` object is always present as `req`.
- `schema_name` (`str`, optional): name of the GraphQL schema from the [Schema Registry](https://tartiflette.io/docs/api/schema-registry/) which should be used — mostly for advanced usage. Defaults to `"default"`.

### Methods

- `__call__(scope, receive, send)`: ASGI3 implementation.

### Error responses

| Status code                | Description                                                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 400 Bad Request            | The GraphQL query could not be found in the request data.                                                                        |
| 404 Not Found              | The request does not match the GraphQL or GraphiQL endpoint paths.                                                               |
| 405 Method Not Allowed     | The HTTP method is not one of `GET`, `HEAD` or `POST`.                                                                           |
| 415 Unsupported Media Type | The POST request made to the GraphQL endpoint uses a `Content-Type` different from `application/json` and `application/graphql`. |

## `GraphiQL`

Configuration helper for the GraphiQL client.

### Parameters

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

## `Subscriptions`

Configuration helper for WebSocket subscriptions.

### Parameters

**Note**: all parameters are keyword-only.

- `path` (`str`): the path of the subscriptions WebSocket endpoint, **relative to the root path which `TartifletteApp` is served at**. If not given, defaults to `/subscriptions`.
