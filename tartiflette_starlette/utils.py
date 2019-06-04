import string


def load_string_template(path: str) -> string.Template:
    with open(path, encoding="utf-8") as tpl_file:
        return string.Template(tpl_file.read())
