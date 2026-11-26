from fastapi import APIRouter, Depends, HTTPException, Query,BackgroundTasks
from app.services.matcher import run_matching_pipeline
from app.database import AsyncSessionLocal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.item import Item
from app.models.user import User
from app.core.sensitive import check_text_safety
from app.schemas.item import ItemCreate, ItemListOut, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemOut)
async def create_item(
    payload: ItemCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 对标题和描述进行安全校验
    check_text_safety(payload.title)
    check_text_safety(payload.description)
    if payload.location:
        check_text_safety(payload.location)

    item = Item(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    # 启动后台任务进行 AI 匹配
    async def background_match():
        async with AsyncSessionLocal() as new_db:
            await run_matching_pipeline(item, new_db)
            
    background_tasks.add_task(background_match)
    
    return ItemOut.model_validate(item)


@router.get("", response_model=ItemListOut)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    type: int | None = Query(None),
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    status: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    conditions = [Item.status == status]
    if type is not None:
        conditions.append(Item.type == type)
    if category:
        conditions.append(Item.category == category)
    if keyword:
        like = f"%{keyword}%"
        conditions.append(or_(Item.title.like(like), Item.description.like(like)))

    total = await db.scalar(select(func.count()).select_from(Item).where(*conditions))
    result = await db.execute(
        select(Item)
        .where(*conditions)
        .order_by(Item.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()
    return ItemListOut(total=total or 0, items=[ItemOut.model_validate(i) for i in items])


@router.get("/mine", response_model=ItemListOut)
async def my_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = await db.scalar(
        select(func.count()).select_from(Item).where(Item.user_id == current_user.id)
    )
    result = await db.execute(
        select(Item)
        .where(Item.user_id == current_user.id)
        .order_by(Item.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = result.scalars().all()
    return ItemListOut(total=total or 0, items=[ItemOut.model_validate(i) for i in items])


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    return ItemOut.model_validate(item)


@router.patch("/{item_id}/close", response_model=ItemOut)
async def close_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    if item.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权操作")
    item.status = 3
    await db.commit()
    await db.refresh(item)
    return ItemOut.model_validate(item)