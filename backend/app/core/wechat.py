import httpx

from app.config import settings


async def code2session(code: str) -> dict:
    """用 wx.login 的 code 换取 openid。开发模式返回 mock openid。"""
    if settings.WECHAT_MOCK:
        return {"openid": "mock_openid_test_user_001"}

    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APPID,
        "secret": settings.WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "openid" not in data:
        raise ValueError(f"wechat login failed: {data}")
    return data