"""Agent 工具集：可被 LLM 调用的业务工具（LangChain Tool 封装）。"""

# 注意：vector_store 在函数内惰性导入，避免 app.memory 与 app.agents 之间
# 顶层循环导入（memory -> agents.base -> agents -> tools -> memory）。
from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str) -> str:
    """根据问题语义检索企业知识库，返回最相关的文档片段。

    在回答涉及企业资料、规范、业务知识的问题时，应优先调用本工具。

    Args:
        query: 用户的问题或检索关键词。
    """
    from app.memory import vector_store  # 惰性导入，避免循环依赖

    results = vector_store.search_sync(query)
    if not results:
        return "知识库中未检索到相关内容。"
    # 拼接为对 LLM 友好的片段文本
    parts = []
    for r in results:
        src = r["metadata"].get("source", "unknown")
        parts.append(f"[来源: {src}]\n{r['content']}")
    return "\n\n---\n\n".join(parts)


@tool
def get_current_datetime() -> str:
    """返回服务器当前时间，用于涉及日期的问答。"""
    from datetime import datetime

    return datetime.now().isoformat()


TOOLS = [search_knowledge_base, get_current_datetime]