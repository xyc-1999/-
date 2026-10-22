"""会话管理路由。"""
from fastapi import APIRouter, Query

from app.memory import session_memory

router = APIRouter()


@router.get("")
async def list_sessions(
    sort: str = Query("recent", pattern="^(recent|oldest|messages)$", description="排序: recent|oldest|messages")
) -> dict:
    items = await session_memory.list_sessions(sort=sort)
    return {"total": len(items), "sort": sort, "sessions": items}


@router.get("/{session_id}/messages")
async def get_messages(session_id: str) -> dict:
    msgs = await session_memory.get_messages(session_id)
    return {"session_id": session_id, "messages": msgs}


@router.post("/{session_id}/clear")
async def clear(session_id: str) -> dict:
    await session_memory.clear(session_id)
    return {"session_id": session_id, "cleared": True}