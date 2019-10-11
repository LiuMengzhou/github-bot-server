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
# 模板必需填写的字段
requiredLabels = [
    "是否为新品",
    # "项目ID",
    # "用户ID",
    "企业名称",
    "环境",
    "现象",
    "期望"
]

# 开发者新建 issue
@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):

    url = event.data["issue"]["url"]
    comments_url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    title = event.data["issue"]["title"]
    body = event.data["issue"]["body"]
    print(f"用户: {author}, issue 地址: {url}")

    message = f"@{author} 感谢您提出宝贵的 issue，但是github issue机制已被废弃，请去小米开发者平台的[工单系统](https://iot.mi.com/fe-op/personalCenter/feedback)提工单。这个 issue 将被关闭，谢谢您的配合！"
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
