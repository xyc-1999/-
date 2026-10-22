"""LangGraph 智能体状态图。

采用典型的 ReAct 风格：Agent 节点决定下一步，
如果产生工具调用则执行工具后回到 Agent，否则结束。
"""
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolExecutor, ToolNode

from app.agents.base import create_chat_model
from app.agents.tools import TOOLS
from app.core.config import settings


class AgentState(TypedDict):
    """图共享状态。消息由 add_messages reducer 累积。"""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str


# 工具执行器：langgraph.prebuilt 自动把 LLM 的工具调用映射到结局函数
tool_executor = ToolExecutor(TOOLS)
tool_node = ToolNode(TOOLS)


def _system_prompt() -> str:
    return (
        "你是一位专业的企业智能助手。请结合会话历史与企业知识库回答用户问题。"
        "遇到需要查资料的问题，务必先调用知识库检索工具。回答应简洁、准确。"
    )


def call_agent(state: AgentState) -> dict:
    """Agent 节点：带历史上下文调用 LLM 并决定意图。"""
    llm = create_chat_model()
    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [SystemMessage(content=_system_prompt())]
    messages.extend(state["messages"])

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", END]:
    """路由：如果 AI 消息包含 tool_calls 则执行工具，否则结束。"""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_graph():
    """构建并编译 LangGraph 图。"""
    graph = StateGraph(AgentState)

    graph.add_node("agent", call_agent)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


agent_app = build_graph()