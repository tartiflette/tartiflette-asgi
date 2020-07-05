import json
import typing

from starlette.background import BackgroundTasks
from starlette.datastructures import QueryParams
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.websockets import WebSocket
from tartiflette import Engine

from ._errors import format_errors
from ._middleware import get_graphql_config
from ._subscriptions import GraphQLWSProtocol


class GraphiQLEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        config = get_graphql_config(request)
        graphql_endpoint = request["root_path"] + config.path
        subscriptions_endpoint = None
        if config.subscriptions:
            subscriptions_endpoint = request["root_path"] + config.subscriptions.path
        graphiql = config.graphiql
        assert graphiql is not None
        html = graphiql.render_template(
            graphql_endpoint=graphql_endpoint,
            subscriptions_endpoint=subscriptions_endpoint,
        )
        return HTMLResponse(html)


class GraphQLEndpoint(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return await self._get_response(request, data=request.query_params)

    async def post(self, request: Request) -> Response:
        content_type = request.headers.get("Content-Type", "")

        if "application/json" in content_type:
            try:
                data = await request.json()
            except json.JSONDecodeError:
                return JSONResponse({"error": "Invalid JSON."}, 400)
        elif "application/graphql" in content_type:
            body = await request.body()
            data = {"query": body.decode()}
        elif "query" in request.query_params:
            data = request.query_params
        else:
            return PlainTextResponse("Unsupported Media Type", 415)

        return await self._get_response(request, data=data)

    async def _get_response(self, request: Request, data: QueryParams) -> Response:
        try:
            query = data["query"]
        except KeyError:
            return PlainTextResponse("No GraphQL query found in the request", 400)

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

        return JSONResponse(content=content, status_code=status, background=background)

    async def dispatch(self) -> None:
        request = Request(self.scope, self.receive)
        graphiql = get_graphql_config(request).graphiql
        if "text/html" in request.headers.get("Accept", ""):
            app: ASGIApp
            if graphiql and graphiql.path is None:
                app = GraphiQLEndpoint
            else:
                app = PlainTextResponse("Not Found", 404)
            await app(self.scope, self.receive, self.send)
        else:
            await super().dispatch()


class SubscriptionEndpoint(WebSocketEndpoint):
    encoding = "json"  # type: ignore

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope, receive, send)
        self.protocol: typing.Optional[GraphQLWSProtocol] = None

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept(subprotocol=GraphQLWSProtocol.name)
        config = get_graphql_config(websocket)
        self.protocol = GraphQLWSProtocol(
            websocket=websocket, engine=config.engine, context=dict(config.context)
        )

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        assert self.protocol is not None
        await self.protocol.on_receive(message=data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        assert self.protocol is not None
        await self.protocol.on_disconnect(close_code)
