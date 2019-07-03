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
        default_variables: dict = None
    ):
        if template is None:
            with open(_GRAPHIQL_TEMPLATE, encoding="utf-8") as f:
                template = f.read()
        self.path = path
        self.template = string.Template(template)
        self.default_variables = default_variables or {}

    def render_template(self, graphql_endpoint_path: str) -> str:
        return self.template.substitute(
            path=graphql_endpoint_path,
            default_variables=json.dumps(self.default_variables),
        )


class GraphQLRequestState(typing.NamedTuple):
    engine: Engine
    graphiql: GraphiQL
    graphql_endpoint_path: str
