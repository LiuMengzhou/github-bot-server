import os

import aiohttp
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

routes = web.RouteTableDef()

router = routing.Router()

user = "LiuMengzhou"


@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """
    Whenever an issue is opened, greet the author and say thanks.
    """
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    title = event.data["issue"]["title"]
    body = event.data["issue"]["body"]

    # message = f"@{author} 感谢您提出宝贵的 issue，我会通知开发尽快处理！"
    message = f"@{author} 感谢您提出宝贵的 issue，我会通知开发尽快处理！\ntitle: @{title}\nbody: @{body}"
    await gh.post(url, data={"body": message})


@routes.post("/")
async def main(request):
    body = await request.read()

    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, user,
                                  oauth_token=oauth_token)
        await router.dispatch(event, gh)
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)
