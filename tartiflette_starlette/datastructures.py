import os
import string

from .utils import load_string_template

CURDIR = os.path.dirname(__file__)


class GraphiQL:
    def __init__(self, path: str = None, template: string.Template = None):
        if template is None:
            template = load_string_template(
                os.path.join(CURDIR, "graphiql.html")
            )
        self.path = path
        self.template = template
