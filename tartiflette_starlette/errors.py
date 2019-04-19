import typing


def _format_error(err: typing.Any) -> dict:
    formatted_error = {"type": "internal_error", "message": "Server internal"}

    if isinstance(err, Exception):
        formatted_error["message"] = str(err)

    return formatted_error


def format_errors(errors: typing.Sequence[typing.Any]) -> typing.List[dict]:
    return [_format_error(error) for error in errors]
