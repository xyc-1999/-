"""LLM / Embedding 工厂。

- 聊天模型：走 OpenAI 兼容协议（DeepSeek 已兼容），统一用 ChatOpenAI。
- 嵌入模型：按 EMBEDDING_PROVIDER 策略切换：
    * dashscope(默认)     : 通义 Qwen 模型（qwen3.7-text-embedding-flash）
    * openai              : OpenAI 官方 embedding
    * sentence_transformers: 本地模型，离线可用。
"""
from functools import lru_cache
from typing import Any

from langchain_openai import ChatOpenAI

from app.core.config import settings


@lru_cache
def create_chat_model(model: str | None = None, temperature: float | None = None) -> ChatOpenAI:
    """创建聊天模型（DeepSeek / 任意 OpenAI 兼容端点）。

    Args:
        model: 覆盖 default 模型，如 deepseek-reasoner。
    """
    return ChatOpenAI(
        model=model or settings.LLM_CHAT_MODEL,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        api_key=settings.LLM_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        timeout=120,
    )


@lru_cache
def create_embeddings() -> Any:
    """按配置创建文本嵌入模型（策略工厂）。

    - dashscope    : 通义 Qwen 模型（默认），OpenAI 兼容端点。
    - openai       : OpenAI 官方 embedding。
    - 其它           : 回退到本地 sentence-transformers，离线可用。
    """
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider in ("dashscope", "openai"):
        from langchain_openai import OpenAIEmbeddings

        # dashscope 与 openai 同为 OpenAI 兼容协议，仅端点/Key/模型不同
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL,
            check_embedding_ctx_length=False,  # 兼容部分网关的长度校验
        )

    # 本地 sentence-transformers
    from langchain_community.embeddings import SentenceTransformerEmbeddings

    return SentenceTransformerEmbeddings(model_name=settings.EMBEDDING_HF_MODEL)