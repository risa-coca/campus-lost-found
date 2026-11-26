from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.item import Item, Claim
from app.models.user import User
from app.core.sensitive import check_text_safety

router = APIRouter(prefix="/claims", tags=["claims"])

class ClaimCreate(BaseModel):
    item_id: int
    answers: str

@router.post("")
async def create_claim(
    payload: ClaimCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await db.get(Item, payload.item_id)
    if not item or item.type != 1:
        raise HTTPException(status_code=400, detail="只能对招领物品发起认领")
    
    if item.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能认领自己发布的物品")

    # 校验认领填写的特征是否合规
    check_text_safety(payload.answers)

    claim = Claim(
        item_id=payload.item_id,
        claimant_id=current_user.id,
        answers=payload.answers
    )
    db.add(claim)
    await db.commit()
    return {"message": "认领申请已提交，等待拾主审核"}

@router.get("/sent")
async def my_sent_claims(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 获取我发起的认领，并联合查询物品信息
    result = await db.execute(
        select(Claim, Item).join(Item, Claim.item_id == Item.id).where(Claim.claimant_id == current_user.id)
    )
    return [{"claim": c.__dict__, "item": i.__dict__} for c, i in result.all()]

@router.get("/received")
async def my_received_claims(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 获取别人对我发布的招领物品发起的认领申请
    result = await db.execute(
        select(Claim, Item, User).join(Item, Claim.item_id == Item.id).join(User, Claim.claimant_id == User.id).where(Item.user_id == current_user.id)
    )
    return [{"claim": c.__dict__, "item": i.__dict__, "user": u.__dict__} for c, i, u in result.all()]

@router.post("/{claim_id}/approve")
async def approve_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = await db.get(Claim, claim_id)
    item = await db.get(Item, claim.item_id)
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    claim.status = 1
    item.status = 2 # 物品状态改为已归还
    await db.commit()
    return {"message": "已同意认领"}

@router.post("/{claim_id}/reject")
async def reject_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = await db.get(Claim, claim_id)
    item = await db.get(Item, claim.item_id)
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    claim.status = 2
    await db.commit()
    return {"message": "已拒绝认领"}

# 确认交接完成
@router.post("/{claim_id}/complete")
async def complete_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = await db.get(Claim, claim_id)
    item = await db.get(Item, claim.item_id)
    if current_user.id != claim.claimant_id and current_user.id != item.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    claim.status = 3 
    item.status = 2  
    await db.commit()
    return {"message": "交接完成"}