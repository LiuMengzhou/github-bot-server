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

    missLabels = []
    for label in requiredLabels:
        if (body.find(label) == -1):
            missLabels.append(label)

    # 是不是按照模板提 issue
    if len(missLabels) == 0:
        message = f"@{author} 感谢您提出宝贵的 issue，我会通知开发尽快处理！以后推荐您到开发者平台[提工单](https://iot.mi.com/fe-op/personalCenter/feedback)，有助于我们更加规范地管理问题，谢谢！"
        await gh.post(comments_url, data={"body": message})
    else:
        message = f"@{author} 感谢您提出宝贵的 issue，但好像您并没有按照模板提出 issue～\n{missLabels}这些必填项希望您能认真填写～\n如果不修改，我们会降低此 issue 的优先级！"
        await gh.post(comments_url, data={"body": message})
        print(f"没有填写的项: {missLabels}")
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
