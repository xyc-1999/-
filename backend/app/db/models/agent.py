"""Agent 定义模型：持久化业务定义的智能体。"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AgentModel(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="Agent 名称")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="用途描述")
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="系统提示词")
    model: Mapped[str] = mapped_column(String(128), nullable=False, default="deepseek-chat", comment="默认模型")
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="active", comment="active|disabled")
    meta: Mapped[str | None] = mapped_column(Text, nullable=True, comment="扩展元信息 JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())