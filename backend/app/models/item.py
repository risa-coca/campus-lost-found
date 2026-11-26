from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        Index("idx_type_category_status", "type", "category", "status"),
        Index("idx_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[int] = mapped_column(nullable=False)  # 0=寻物 1=招领
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    location: Mapped[str] = mapped_column(String(128), nullable=True, default="")
    event_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[int] = mapped_column(default=0)  # 0待匹配 1已匹配 2已归还 3已关闭
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lost_item_id: Mapped[int] = mapped_column(nullable=False)
    found_item_id: Mapped[int] = mapped_column(nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(nullable=False)
    claimant_id: Mapped[int] = mapped_column(nullable=False)
    answers: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(nullable=False)
    receiver_id: Mapped[int] = mapped_column(nullable=False)
    item_id: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())