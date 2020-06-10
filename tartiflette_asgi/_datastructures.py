import inspect
import json
import os
import string
import typing

from tartiflette import Engine

_GRAPHIQL_TEMPLATE = os.path.join(os.path.dirname(__file__), "graphiql.html")


def _optional(value: typing.Optional[str]) -> str:
    return value if value is not None else ""


class Subscriptions:
    def __init__(self, *, path: str) -> None:
        self.path = path


class GraphiQL:
    def __init__(
        self,
        *,
        path: str = None,
        template: str = None,
        default_query: str = "",
        default_variables: dict = None,
        default_headers: dict = None,
    ):
        if template is None:
            with open(_GRAPHIQL_TEMPLATE, encoding="utf-8") as f:
                template = f.read()
        self.path = path
        self.template = string.Template(template)
        self.default_query = inspect.cleandoc(default_query)
        self.default_variables = default_variables or {}
        self.default_headers = default_headers or {}

    def render_template(
        self, graphql_endpoint: str, subscriptions_endpoint: typing.Optional[str]
    ) -> str:
        return self.template.substitute(
            endpoint=graphql_endpoint,
            subscriptions_endpoint=_optional(subscriptions_endpoint),
            default_query=self.default_query,
            default_variables=json.dumps(self.default_variables),
            default_headers=json.dumps(self.default_headers),
        )


class GraphQLConfig(typing.NamedTuple):
    engine: Engine
    context: dict
    graphiql: typing.Optional[GraphiQL]
    path: str
    subscriptions: typing.Optional[Subscriptions]
