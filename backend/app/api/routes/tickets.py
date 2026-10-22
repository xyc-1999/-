"""工单路由：查询当前用户的工单列表(MySQL)。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ticket import Ticket
from app.db.session import get_db

router = APIRouter()


def _serialize(t: Ticket) -> dict:
    return {
        "id": t.id,
        "user_id": t.user_id,
        "subject": t.subject,
        "content": t.content,
        "priority": t.priority,
        "status": t.status,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.get("", description="获取当前用户最新工单列表")
async def list_tickets(
    db: Session = Depends(get_db),
    user_id: str = Query("demo-user-001", description="用户标识"),
    limit: int = Query(20, ge=1, le=50),
) -> dict:
    stmt = (
        select(Ticket)
        .where(Ticket.user_id == user_id)
        .order_by(Ticket.created_at.desc())
        .limit(limit)
    )
    rows = db.scalars(stmt).all()
    return {"user_id": user_id, "total": len(rows), "tickets": [_serialize(t) for t in rows]}