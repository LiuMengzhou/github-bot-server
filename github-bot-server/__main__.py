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
    "是否为新品（必填）",
    "项目ID（必填）",
    "企业名称（必填）",
    "环境（必填）",
    "现象（必填）",
    "期望（必填）"
]

# 开发者新建 issue
@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):

    url = event.data["issue"]["url"]
    comments_url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    title = event.data["issue"]["title"]
    body = event.data["issue"]["body"]

    # 是不是按照模板提 issue
    isIssueTemplateMatched = all(body.find(label) for label in requiredLabels)

    if isIssueTemplateMatched:
        message = f"@{author} 感谢您提出宝贵的 issue，我会通知开发尽快处理！"
        await gh.post(comments_url, data={"body": message})
    else:
        message = f"@{author} 感谢您提出宝贵的 issue\n但好像您并没有按照模板提出 issue，希望您能填写所有的必填项\n如果不修改，我们会降低此 issue 的优先级！"
        await gh.post(comments_url, data={"body": message})
        # await gh.patch(url, data={"state": "closed"})


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
