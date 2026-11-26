from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.item import Item, Match
from app.models.user import User
from app.core.llm import extract_item_attributes
from app.core.retriever import find_candidates
from app.core.notify import send_subscribe_message
from app.config import settings # 新增：导入配置
import requests

async def run_matching_pipeline(item: Item, db: AsyncSession):
    """异步执行匹配管线"""
    # 1. 属性抽取
    attrs = extract_item_attributes(item.title, item.description)
    
    # 2. 混合召回
    candidates = await find_candidates(db, item)
    
    # 3. 生成解释并入库
    for candidate, score in candidates:
        if score < 0.6: # 阈值过滤
            continue
            
        # 调用大模型生成匹配解释
        prompt = f"""
        系统发现两条可能匹配的记录。
        寻物：{item.title} - {item.description}
        招领：{candidate.title} - {candidate.description}
        请用一句话向用户解释为什么它们可能是同一个东西（比如颜色、地点、独特标记相同）。
        """
        try:
            resp = requests.post("http://127.0.0.1:11434/api/generate", json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False
            })
            explanation = resp.json().get("response", "特征相似，建议核实。").strip()
        except:
            explanation = "特征描述高度相似，建议进一步核实。"
            
        # 判断谁是 lost，谁是 found
        lost_id = item.id if item.type == 0 else candidate.id
        found_id = item.id if item.type == 1 else candidate.id
        
        # 防重复插入
        existing = await db.execute(
            select(Match).where(Match.lost_item_id == lost_id, Match.found_item_id == found_id)
        )
        
        if not existing.scalar_one_or_none():
            new_match = Match(
                lost_item_id=lost_id,
                found_item_id=found_id,
                score=round(score * 100, 2),
                explanation=explanation
            )
            db.add(new_match)
            
            # ==========================================
            # 新增：发送订阅消息通知给被匹配方
            # ==========================================
            # candidate 是数据库里原有的记录，我们要通知 candidate 的发布者
            target_user = await db.get(User, candidate.user_id)
            if target_user and target_user.openid:
                # 调用通知发送服务
                await send_subscribe_message(
                    openid=target_user.openid,
                    template_id=settings.WECHAT_TEMPLATE_MATCH, # 需要你在 .env 和 config.py 配置
                    data={
                        "thing1": {"value": item.title[:20]}, # 模板要求：物品名称
                        "phrase2": {"value": "系统发现匹配线索"}, # 模板要求：状态
                        "time3": {"value": "刚刚"}            # 模板要求：时间
                    },
                    # 点击消息跳转到详情页
                    page=f"pages/detail/detail?id={item.id}"
                )
    
    await db.commit()