import base64
import os

import aiohttp
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio

routes = web.RouteTableDef()

router = routing.Router()

# 机器人的 github username
user = "MIoTBot"
# miot-plugin-sdk repo webhooks secret
secret = "dHMgaXMgYSBwaXR5"
# 机器人的 github personal token
oauth_token = base64.b64decode(
    "YWE5ZGNmMGYzMWQ2ZDI5NzZiNmMzMjQwMGIzMWFjNzk4YjY0MzEyNg==").decode("utf-8")

# 开发者新建 issue
@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):

    url = event.data["issue"]["url"]
    comments_url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    title = event.data["issue"]["title"]
    body = event.data["issue"]["body"]

    # 是不是按照模板提 issue
    isIssueTemplateMatched = body.find(
        "是否为新品") != -1 and body.find("填 新品 or 在售") == -1

    if isIssueTemplateMatched:
        message = f"@{author} 感谢您提出宝贵的 issue，我会通知开发尽快处理！"
        await gh.post(comments_url, data={"body": message})
    else:
        message = f"@{author} 感谢您提出宝贵的 issue\n但好像您并没有按照模板提出 issue，希望您能填写所有的必填项\n该 issue 将被 close！"
        await gh.post(comments_url, data={"body": message})
        await gh.patch(url, data={"state": "closed"})


@routes.post("/")
async def main(request):
    body = await request.read()
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
