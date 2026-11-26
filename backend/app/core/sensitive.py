import re
from fastapi import HTTPException

# 1. 基础违规词库（你可以根据实际情况不断扩充，生产环境建议接入第三方敏感词库）
BANNED_WORDS = {
    "傻逼", "操你妈", "代考", "代写", "博彩", "赌博", 
    "色情", "黄片", "约炮", "毒品", "枪支", "办证"
}

def check_text_safety(text: str) -> None:
    """检查文本是否包含敏感词或联系方式，违规直接抛出 400 异常"""
    if not text:
        return

    # --- 1. 违规词检查 ---
    for word in BANNED_WORDS:
        if word in text:
            raise HTTPException(
                status_code=400, 
                detail=f"发布内容包含违规词汇（{word}），请修改后重试。"
            )

    # --- 2. 联系方式防泄漏（正则拦截） ---
    # 拦截连续 8 位以上的数字（防手机号、QQ号）
    if re.search(r'\d{8,}', text):
        raise HTTPException(
            status_code=400, 
            detail="请勿在描述中直接填写手机号、QQ号等联系方式，以防隐私泄露。认证时会通过系统通知联系您。"
        )
        
    # 拦截微信号、加V等引流词汇
    if re.search(r'(微信号|加微|加v|vx|wx)', text, re.IGNORECASE):
        raise HTTPException(
            status_code=400, 
            detail="请勿在描述中留下微信号或引流信息。"
        )

    # --- 3. 微信官方内容安全接口（生产环境必做，开发环境跳过） ---
    # 如果你申请了真实的小程序 AppID，强烈建议开启此校验，微信官方会自动识别涉黄涉政内容
    # from app.config import settings
    # if not settings.WECHAT_MOCK:
    #     # 调用微信 security.msgSecCheck 接口
    #     # 如果返回未通过，抛出 HTTPException