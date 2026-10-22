"""会话记录模型：用于历史审计与续接。"""
from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SessionRecord(Base):
    __tablename__ = "session_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="会话ID")
    agent_id: Mapped[int | None] = mapped_column(nullable=True, comment="关联 Agent")
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="用户标识")
    role: Mapped[str] = mapped_column(String(16), nullable=False, comment="user|assistant|tool")
    content: Mapped[str] = mapped_column(comment="消息内容，JSON 序列化")
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="扩展信息")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())