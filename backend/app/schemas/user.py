from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    code: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str | None = None
    avatar_url: str | None = None
    role: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut

class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None