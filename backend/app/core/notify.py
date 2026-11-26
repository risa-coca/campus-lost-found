import httpx
from app.config import settings

async def send_subscribe_message(openid: str, template_id: str, data: dict, page: str = "pages/index/index"):
    """发送订阅消息"""
    if settings.WECHAT_MOCK:
        print(f"[Mock 订阅消息] 发送给 {openid}，模板: {template_id}，数据: {data}")
        return True

    url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send"
    payload = {
        "touser": openid,
        "template_id": template_id,
        "page": page,
        "data": data
    }
    # 注：实际生产环境需要获取 access_token，这里暂略 token 获取环节
    # async with httpx.AsyncClient() as client:
    #     resp = await client.post(url, json=payload)
    #     return resp.json().get("errcode") == 0
    return True