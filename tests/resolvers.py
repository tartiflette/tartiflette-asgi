from tartiflette import Resolver
from starlette.requests import Request


@Resolver("Query.hello")
async def hello(parent, args, context, info) -> str:
    name = args.get("name", "stranger")
    return "Hello " + name


@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info) -> str:
    request: Request = context["req"]
    user = request.state.user
    return "a mystery" if user is None else user


@Resolver("Query.foo")
async def resolve_foo(parent, args, context, info) -> str:
    get_foo = context.get("get_foo", lambda: "default")
    return get_foo()
