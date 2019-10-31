# FAQ

## What is ASGI?

ASGI provides a standard interface between async-capable Python web servers, frameworks, and applications. An ASGI application is a callable with the following signature:

```python
async def app(scope, receive, send) -> None:
    ...
```

For more information, see the [ASGI documentation](https://asgi.readthedocs.io/en/latest/) and this list of [publications about ASGI](https://github.com/florimondmanca/awesome-asgi#publications).

## Do I need to learn GraphQL/Tartiflette to use this package?

**Yes**: once you've got the `TartifletteApp` ASGI app up and running, you're in Tartiflette territory.

Here are some resources to get you started:

- [Tartiflette tutorial](https://tartiflette.io/docs/tutorial/getting-started)
- [Introduction to GraphQL](https://graphql.org/learn/)
- [Tartiflette API reference](https://tartiflette.io/docs/api/engine)

## Does this package ship with Tartiflette?

**Yes**. Everything is included, which allows you to start building your GraphQL API right away. See also [Installation](#installation).

## What is the role of Starlette?

`tartiflette-asgi` uses Starlette as a lightweight ASGI toolkit: internally, it uses Starlette's request and response classes, and some other components.

Luckily, this does not require your applications to use Starlette at all.

For example, if you are [submounting your GraphQL app](#submounting-on-another-asgi-app) on an app built with an async web framework, this framework does not need to use Starlette — it just needs to speak ASGI.
