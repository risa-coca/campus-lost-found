from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_admin
from app.models.item import Item, Match, Claim
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])

@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_users = await db.scalar(select(func.count()).select_from(User))
    total_items = await db.scalar(select(func.count()).select_from(Item))
    returned_items = await db.scalar(select(func.count()).select_from(Item).where(Item.status == 2))
    pending_claims = await db.scalar(select(func.count()).select_from(Claim).where(Claim.status == 0))
    
    return {
        "total_users": total_users or 0,
        "total_items": total_items or 0,
        "returned_items": returned_items or 0,
        "pending_claims": pending_claims or 0
    }

@router.get("/items")
async def list_all_items(db: AsyncSession = Depends(get_db)):
    # 后台获取所有物品
    result = await db.execute(select(Item).order_by(Item.created_at.desc()).limit(100))
    return [item.__dict__ for item in result.scalars().all()]

@router.get("/claims")
async def list_all_claims(db: AsyncSession = Depends(get_db)):
    # 获取所有待审核的认领
    result = await db.execute(
        select(Claim, Item).join(Item, Claim.item_id == Item.id).where(Claim.status == 0)
    )
    return [{"claim": c.__dict__, "item": i.__dict__} for c, i in result.all()]