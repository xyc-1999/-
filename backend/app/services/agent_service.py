"""Agent 服务：整合 会话记忆(Redis) + 图执行(LangGraph) + 落库(MySQL)。"""
from typing import AsyncIterator

from langchain_core.messages import HumanMessage

from app.agents.graph import agent_app
from app.memory import session_memory


class AgentService:
    """对外提供一次性对话能力，依据 session_id 维护上下文。"""

    async def chat(self, session_id: str, user_input: str) -> str:
        # 1. 读取历史记忆（Redis），构建最长记忆窗口
        history = await session_memory.build_chat_history(session_id)

        # 2. 存入新的人类消息
        await session_memory.add_message(session_id, "user", user_input)

        # 3. 组装 LangGraph 初始状态并执行
        messages = [HumanMessage(content=h["content"]) for h in history]
        messages.append(HumanMessage(content=user_input))

        result = await agent_app.ainvoke({"messages": messages, "session_id": session_id})

        # 4. 取最后一条 assistant 消息作为回复
        final = result["messages"][-1]
        reply = getattr(final, "content", "") or str(final)

        # 5. 异步把模型回复写入记忆
        await session_memory.add_message(session_id, "assistant", reply)
        return reply

    async def stream(self, session_id: str, user_input: str) -> AsyncIterator[str]:
        """流式对话：逐 token 产出最终回答文本。

        通过 LangGraph astream_events 监听 chat model 的流式事件，
        将增量文本实时 yield，便于前端 SSE 展示打字机效果。
        """
        history = await session_memory.build_chat_history(session_id)
        await session_memory.add_message(session_id, "user", user_input)

        messages = [HumanMessage(content=h["content"]) for h in history]
        messages.append(HumanMessage(content=user_input))

        collected: list[str] = []

        async for event in agent_app.astream_events(
            {"messages": messages, "session_id": session_id},
            version="v2",
        ):
            kind = event.get("event")
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                text = getattr(chunk, "content", "")
                if text:
                    collected.append(text)
                    yield text

        # 将完整回复写入记忆，保证会话连续
        await session_memory.add_message(session_id, "assistant", "".join(collected))


agent_service = AgentService()