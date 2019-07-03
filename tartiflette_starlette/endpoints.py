from starlette.background import BackgroundTasks
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from tartiflette import Engine

from .errors import format_errors
from .helpers import StateHelper


class GraphiQLEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        state = StateHelper.get(request)
        html = state.graphiql.render_template(
            graphql_endpoint_path=state.graphql_endpoint_path
        )
        return HTMLResponse(html)


class GraphQLEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return await self._get_response(request, data=request.query_params)

    async def post(self, request: Request) -> Response:
        content_type = request.headers.get("Content-Type", "")

        if "application/json" in content_type:
            data = await request.json()
        elif "application/graphql" in content_type:
            body = await request.body()
            data = {"query": body.decode()}
        elif "query" in request.query_params:
            data = request.query_params
        else:
            return PlainTextResponse("Unsupported Media Type", 415)

        return await self._get_response(request, data=data)

    async def _get_response(self, request: Request, data: dict) -> Response:
        try:
            query = data["query"]
        except KeyError:
            return PlainTextResponse(
                "No GraphQL query found in the request", 400
            )

        background = BackgroundTasks()
        context = {"req": request, "background": background}

        state = StateHelper.get(request)
        engine: Engine = state.engine
        result: dict = await engine.execute(
            query,
            context=context,
            variables=data.get("variables"),
            operation_name=data.get("operationName"),
        )

        content = {"data": result["data"]}
        has_errors = "errors" in result
        if has_errors:
            content["errors"] = format_errors(result["errors"])
        status = 400 if has_errors else 200

        return JSONResponse(
            content=content,
            status_code=status,
            background=context["background"],
        )

    async def dispatch(self):
        request = Request(self.scope, self.receive)
        state = StateHelper.get(request)
        if "text/html" in request.headers.get("Accept", ""):
            if state.graphiql and state.graphiql.path is None:
                app = GraphiQLEndpoint
            else:
                app = PlainTextResponse("Not Found", 404)
            await app(self.scope, self.receive, self.send)
        else:
            await super().dispatch()
