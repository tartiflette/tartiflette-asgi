from tartiflette import Resolver
from starlette.requests import Request

DATA = {"message": "Lazy dog"}


@Resolver("Query.hello")
async def hello(parent, args, ctx, info) -> str:
    name = args.get("name", "stranger")
    return "Hello " + name


@Resolver("Query.whoami")
async def resolve_whoami(parent, args, ctx, info) -> str:
    request: Request = ctx["req"]
    user = request.state.user
    return "a mystery" if user is None else user


@Resolver("Query.message")
async def resolve_message(parent, args, ctx, info) -> str:
    return ctx.get("message", DATA["message"])


@Resolver("Mutation.setMessage")
async def set_message(parent, args, ctx, info):
    message = args["input"]["message"]
    ctx["message"] = message  # Shouldn't affect context in other requests
    DATA["message"] = message
    return message
