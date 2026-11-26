from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.core.retriever import embedder
from app.core.vision import analyze_image_with_glm # 🔥 引入视觉接口
from app.models.item import Item
import requests

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    image_url: str | None = None

@router.post("")
async def chat_assistant(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    search_query = payload.query

    # 1. 如果用户发了图片，调用视觉大模型识别
    if payload.image_url:
        image_description = analyze_image_with_glm(payload.image_url)
        if image_description:
            search_query = f"用户上传了物品图片，AI识别描述为：{image_description}。用户原话：{payload.query}"
        else:
            return {"reply": "抱歉，图片识别服务暂时不可用，请尝试用文字描述您丢失的物品。", "matches": []}

    # 2. 向量检索
    query_vec = embedder.encode(search_query, normalize_embeddings=True)
    result = await db.execute(select(Item).where(Item.status == 0).order_by(Item.created_at.desc()).limit(100))
    items = result.scalars().all()
    
    scored = []
    for i in items:
        i_vec = embedder.encode(f"{i.title} {i.description}", normalize_embeddings=True)
        score = float(query_vec @ i_vec)
        scored.append((i, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    top_items = [i for i, s in scored[:3] if s > 0.5] # 取最相似的前3个
    
    # 3. 构造上下文
    context = "\n".join([f"物品：{i.title}，描述：{i.description}，地点：{i.location}" for i in top_items])
    if not context:
        context = "没有找到高度相关的记录。"

    # 4. 调用本地 Qwen 生成最终回答
    prompt = f"""
    你是校园失物招领助手。用户的搜索意图是：{search_query}
    以下是数据库中可能相关的记录：
    {context}
    
    请根据上述记录，用一两句简短的话回答用户。如果匹配，直接告诉他找到了什么线索；如果不匹配，直接说没找到。不要编造物品细节，不要发散。
    """
    
    try:
        resp = requests.post("http://127.0.0.1:11434/api/generate", json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        })
        reply = resp.json().get("response", "抱歉，我暂时离线了。").strip()
    except:
        reply = "抱歉，AI 文本生成服务暂时无法连接。"
        
    # 🔥 5. 组装完整的卡片信息
    match_items = []
    for i in top_items:
        match_items.append({
            "id": i.id,
            "title": i.title,
            "description": i.description,
            "location": i.location,
            "image_url": i.image_url,
            "type": i.type
        })

    return {"reply": reply, "matches": match_items}