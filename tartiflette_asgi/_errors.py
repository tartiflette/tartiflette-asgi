import ast
import typing


def _format_error(error: typing.Any) -> dict:
    try:
        return ast.literal_eval(str(error))
    except ValueError:
        return {"message": "Internal Server Error"}


def format_errors(errors: typing.Sequence[typing.Any]) -> typing.List[dict]:
    return [_format_error(error) for error in errors]
