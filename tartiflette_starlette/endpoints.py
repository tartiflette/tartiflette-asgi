import typing

from starlette.background import BackgroundTasks
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from starlette.websockets import WebSocket
from tartiflette import Engine

from .errors import format_errors
from .middleware import get_graphql_config
from .subscriptions import GraphQLWSProtocol


class GraphiQLEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        config = get_graphql_config(request)
        html = config.graphiql.render_template(
            graphql_endpoint=config.path,
            subscriptions_endpoint=(
                None
                if config.subscriptions is None
                else config.subscriptions.path
            ),
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

        config = get_graphql_config(request)
        background = BackgroundTasks()
        context = {"req": request, "background": background, **config.context}

        engine: Engine = config.engine
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
        graphiql = get_graphql_config(request).graphiql
        if "text/html" in request.headers.get("Accept", ""):
            if graphiql and graphiql.path is None:
                app = GraphiQLEndpoint
            else:
                app = PlainTextResponse("Not Found", 404)
            await app(self.scope, self.receive, self.send)
        else:
            await super().dispatch()


class SubscriptionEndpoint(WebSocketEndpoint):
    encoding = "json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = None

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept(subprotocol=GraphQLWSProtocol.name)
        config = get_graphql_config(websocket)
        self.protocol = GraphQLWSProtocol(
            websocket=websocket,
            engine=config.engine,
            context=dict(config.context),
        )

    async def on_receive(self, websocket: WebSocket, data: typing.Any):
        await self.protocol.on_receive(message=data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        await self.protocol.on_disconnect(close_code)
