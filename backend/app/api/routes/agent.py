"""Agent 会话路由：对话入口。"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, description="与智能体进行一次对话")
async def chat(req: ChatRequest) -> ChatResponse:
    reply = await agent_service.chat(req.session_id, req.message)
    return ChatResponse(session_id=req.session_id, reply=reply)


@router.post("/chat/stream", description="与智能体流式对话（SSE）")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    async def event_gen():
        async for token in agent_service.stream(req.session_id, req.message):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )