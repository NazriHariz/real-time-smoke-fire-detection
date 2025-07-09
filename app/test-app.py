from litestar import Litestar, get, Response

@get("/")
async def index() -> Response:
    return Response(content={"message": "kamil, ex athirah!"})

app = Litestar(route_handlers=[index])

