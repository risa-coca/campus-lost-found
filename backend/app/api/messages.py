from fastapi import APIRouter, Depends
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.api.deps import get_db, get_current_user
from app.models.item import Message, Item, Claim
from app.models.user import User
from sqlalchemy import select, or_, and_, update, func

router = APIRouter(prefix="/messages", tags=["messages"])

class MessageCreate(BaseModel):
    receiver_id: int
    item_id: int
    content: str

@router.post("")
async def send_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = Message(
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        item_id=payload.item_id,
        content=payload.content
    )
    db.add(msg)
    await db.commit()
    return {"message": "发送成功"}

@router.get("/history")
async def get_history(
    receiver_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
     # 把对方发给我的消息标记为已读
    update_stmt = (
        update(Message)
        .where(
            Message.item_id == item_id,
            Message.sender_id == receiver_id,
            Message.receiver_id == current_user.id,
            Message.is_read == 0
        )
        .values(is_read=1)
    )
    await db.execute(update_stmt)
    await db.commit()

    result = await db.execute(
        select(Message).where(
            Message.item_id == item_id,
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == receiver_id),
                and_(Message.sender_id == receiver_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.asc())
    )
    return result.scalars().all()

@router.get("/conversations")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Message).where(
            or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
        ).order_by(Message.created_at.desc())
    )
    msgs = result.scalars().all()
    
    convs = {}
    for m in msgs:
        other_id = m.receiver_id if m.sender_id == current_user.id else m.sender_id
        key = f"{other_id}_{m.item_id}"
        if key not in convs:
            user = await db.get(User, other_id)
            item = await db.get(Item, m.item_id)
            
            # 🔥 统计该会话的未读数
            unread_result = await db.execute(
                select(func.count()).select_from(Message).where(
                    Message.item_id == m.item_id,
                    Message.sender_id == other_id,
                    Message.receiver_id == current_user.id,
                    Message.is_read == 0
                )
            )
            unread_count = unread_result.scalar() or 0
            
            convs[key] = {
                "other_id": other_id,
                "other_name": user.nickname or "校园用户",
                "avatar_url": user.avatar_url if user else None,
                "item_id": m.item_id,
                "item_title": item.title if item else "未知物品",
                "last_msg": m.content,
                "time": m.created_at,
                "unread_count": unread_count  # 🔥 返回未读数
            }
    return list(convs.values())

# 新增一个获取全局未读总数的接口（给底部导航栏用）
@router.get("/unread_total")
async def get_unread_total(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(func.count()).select_from(Message).where(
            Message.receiver_id == current_user.id,
            Message.is_read == 0
        )
    )
    return {"count": result.scalar() or 0}