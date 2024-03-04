# Don't Remove Credit @Codeflix-Bots
# Subscribe Telegram Channel For Amazing Bot @Codeflix_Bots
# Ask Doubt on telegram @sewxiy

from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Codeflix_Bots")


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app
