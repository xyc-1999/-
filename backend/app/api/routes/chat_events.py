"""EventSource 兼容的 SSE 对话端点：GET /api/v1/chat

EventSource 仅支持 GET，故对话参数经 query string 传递。
后端复用 agent_service.stream 流式语言模型输出，逐 token 以 SSE data 帧推送。
"""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.services.agent_service import agent_service

router = APIRouter()


@router.get("/chat", description="EventSource 兼容的流式对话(SSE, GET)")
async def chat_events(
    session_id: str = Query(...),
    message: str = Query(...),
) -> StreamingResponse:
    async def event_gen():
        async for token in agent_service.stream(session_id, message):
            yield f"data: {token}\n\n"
        yield "event: end\ndata: [DONE]\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )