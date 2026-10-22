"""对话相关的 Pydantic 模型。"""
from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(description="会话ID，同一会话可续接上下文")
    message: str = Field(min_length=1, max_length=8000, description="用户消息")
    agent_id: Optional[int] = Field(default=None, description="指定使用哪个 Agent")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    usage: dict = Field(default_factory=dict)