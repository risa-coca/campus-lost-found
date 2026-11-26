import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item

# 全局加载模型，避免重复初始化
print("正在加载嵌入模型 bge-small-zh-v1.5...")
embedder = SentenceTransformer('BAAI/bge-small-zh-v1.5')
print("模型加载完毕。")

async def find_candidates(db: AsyncSession, new_item: Item) -> list[tuple[Item, float]]:
    """找出最相似的候选物品"""
    # 1. 构造查询文本（标题 + 描述）
    query_text = f"{new_item.title} {new_item.description}"
    query_vec = embedder.encode(query_text, normalize_embeddings=True)
    
    # 2. 从 MySQL 中获取相反的记录（如果是寻物，就查招领；反之亦然）
    opposite_type = 1 if new_item.type == 0 else 0
    result = await db.execute(
        select(Item).where(Item.type == opposite_type, Item.status == 0)
    )
    candidates = result.scalars().all()
    
    if not candidates:
        return []
        
    # 3. 计算向量相似度
    scored_candidates = []
    for c in candidates:
        # 这里为了演示，直接实时计算。生产环境可以缓存向量。
        c_text = f"{c.title} {c.description}"
        c_vec = embedder.encode(c_text, normalize_embeddings=True)
        # 余弦相似度
        score = np.dot(query_vec, c_vec)
        scored_candidates.append((c, float(score)))
        
    # 4. 根据分数降序排序，取 Top 5
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    return scored_candidates[:5]