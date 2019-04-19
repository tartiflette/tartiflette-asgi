from tartiflette import Resolver


@Resolver("Query.hello")
async def hello(parent, args, context, info) -> str:
    name = args.get("name", "stranger")
    return "Hello " + name


@Resolver("Query.whoami")
async def resolve_whoami(parent, args, context, info) -> str:
    request = context["request"]
    return "a mystery" if request["user"] is None else request["user"]
