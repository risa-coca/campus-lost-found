from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.models.item import Match, Item
from pydantic import BaseModel

router = APIRouter(prefix="/matches", tags=["matches"])

class MatchOut(BaseModel):
    id: int
    lost_item_id: int
    found_item_id: int
    score: float
    explanation: str | None
    
    class Config:
        from_attributes = True

@router.get("/item/{item_id}", response_model=list[MatchOut])
async def get_item_matches(item_id: int, db: AsyncSession = Depends(get_db)):
    # 获取与该物品相关的所有匹配
    result = await db.execute(
        select(Match).where((Match.lost_item_id == item_id) | (Match.found_item_id == item_id))
    )
    return result.scalars().all()