import hashlib
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.deps import get_db, get_current_user 
from app.core.security import create_access_token
from app.core.wechat import code2session
from app.models.user import User

from app.schemas.user import LoginRequest, LoginResponse, UserOut, UserUpdate 

router = APIRouter(prefix="/auth", tags=["auth"])

class AdminLoginRequest(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    """简单的 SHA256 加密"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@router.post("/admin_login", response_model=LoginResponse)
async def admin_login(payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. 查找账号
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")
        
    # 2. 校验密码
    if user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=400, detail="账号或密码错误")
        
    # 3. 校验是否为管理员
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="该账号无管理员权限")
        
    # 4. 生成 Token 返回
    token = create_access_token(user.id)
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        session_data = await code2session(payload.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    openid = session_data["openid"]

    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(openid=openid, nickname="校园用户")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token(user.id)
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.patch("/profile", response_model=UserOut)
async def update_profile(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
        
    await db.commit()
    await db.refresh(current_user)
    return UserOut.model_validate(current_user)

# 账号注册请求模型
class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str

# 1. 账号注册接口
@router.post("/register", response_model=LoginResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 检查账号是否已存在
    result = await db.execute(select(User).where(User.username == payload.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该账号已被注册")
    
    # 创建新用户 (生成一个临时的 openid 用于区分)
    import uuid
    new_user = User(
        openid=f"local_{uuid.uuid4().hex[:10]}", 
        username=payload.username,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        role="user"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # 注册成功直接发 Token 登录
    token = create_access_token(new_user.id)
    return LoginResponse(token=token, user=UserOut.model_validate(new_user))

# 2. 账号密码登录接口（供前端登录页调用）
class AccountLoginRequest(BaseModel):
    username: str
    password: str

@router.post("/account_login", response_model=LoginResponse)
async def account_login(payload: AccountLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    
    if not user or user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=400, detail="账号或密码错误")
        
    token = create_access_token(user.id)
    return LoginResponse(token=token, user=UserOut.model_validate(user))

