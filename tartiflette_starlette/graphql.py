import os
import string

from starlette import status
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from tartiflette import Engine

from .errors import format_errors

CURDIR = os.path.dirname(__file__)

with open(os.path.join(CURDIR, "graphiql.html")) as tpl_file:
    GRAPHIQL_TEMPLATE = string.Template(tpl_file.read())


async def _handle_graphiql(request: Request) -> Response:
    text = GRAPHIQL_TEMPLATE.substitute(path=request.url.path)
    return HTMLResponse(text)


async def handle_graphql(
    request: Request, engine: Engine, enable_graphiql: bool
) -> Response:
    data: dict

    if request.method in ("GET", "HEAD"):
        if "text/html" in request.headers.get("Accept", ""):
            if not enable_graphiql:
                return PlainTextResponse(
                    "Not Found", status_code=status.HTTP_404_NOT_FOUND
                )
            return await _handle_graphiql(request)

        data = request.query_params

    elif request.method == "POST":
        content_type = request.headers.get("Content-Type", "")

        if "application/json" in content_type:
            data = await request.json()
        elif "application/graphql" in content_type:
            body: bytes = await request.body()
            text = body.decode()
            data = {"query": text}
        elif "query" in request.query_params:
            data = request.query_params
        else:
            return PlainTextResponse(
                "Unsupported Media Type",
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

    else:
        return PlainTextResponse(
            "Method Not Allowed", status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        query = data["query"]
    except KeyError:
        return PlainTextResponse(
            "No GraphQL query found in the request",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    variables = data.get("variables")
    operation_name = data.get("operationName")

    background = BackgroundTasks()

    # Passed as `context` to Tartiflette resolvers.
    # See: https://tartiflette.io/docs/api/resolver
    # Inspired by: https://www.starlette.io/graphql/
    context = {"request": request, "background": background}

    result: dict = await engine.execute(
        query,
        variables=variables,
        context=context,
        operation_name=operation_name,
    )

    has_errors = "errors" in result
    error_data = format_errors(result["errors"]) if has_errors else None
    response_data = {"data": result["data"], "errors": error_data}
    status_code = (
        status.HTTP_400_BAD_REQUEST if has_errors else status.HTTP_200_OK
    )

    return JSONResponse(
        response_data, status_code=status_code, background=background
    )
