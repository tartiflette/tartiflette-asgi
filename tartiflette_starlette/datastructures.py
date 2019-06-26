import os
import string

_GRAPHIQL_TEMPLATE = os.path.join(os.path.dirname(__file__), "graphiql.html")


class GraphiQL:
    def __init__(self, *, path: str = None, template: str = None):
        if template is None:
            with open(_GRAPHIQL_TEMPLATE, encoding="utf-8") as f:
                template = f.read()
        self.path = path
        self.template = string.Template(template)
