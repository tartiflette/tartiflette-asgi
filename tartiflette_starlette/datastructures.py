import inspect
import json
import os
import string
import typing

from tartiflette import Engine

_GRAPHIQL_TEMPLATE = os.path.join(os.path.dirname(__file__), "graphiql.html")


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

    def render_template(self, graphql_endpoint_path: str) -> str:
        return self.template.substitute(
            endpoint=graphql_endpoint_path,
            default_query=self.default_query,
            default_variables=json.dumps(self.default_variables),
            default_headers=json.dumps(self.default_headers),
        )


class GraphQLConfig(typing.NamedTuple):
    engine: Engine
    graphiql: GraphiQL
    graphql_endpoint_path: str
