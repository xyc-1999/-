"""客户工单模型：记录用户工单/服务单数据。"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="用户标识")
    subject: Mapped[str] = mapped_column(String(255), nullable=False, comment="工单主题")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="工单描述")
    priority: Mapped[str] = mapped_column(String(16), default="normal", comment="low|normal|high|urgent")
    status: Mapped[str] = mapped_column(String(16), default="open", comment="open|processing|resolved|closed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )