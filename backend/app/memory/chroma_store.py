"""ChromaDB 向量库封装——用于企业知识库的长期记忆与语义检索。

支持两种模式：
1) 内嵌模式（默认）：数据持久化到 本地目录；
2) Server 模式：配置 CHROMA_HOST 后走 HTTP 连接。
"""
import os
from typing import Any

from app.core.config import settings
from langchain_chroma import Chroma

from app.agents.base import create_embeddings

# 部分 embedding 供应商（如 DashScope 兼容网关）单次批量上限 20，
# 大文档切分后分片较多，需分批写入，避免超出批量限制而入库失败。
_EMBED_BATCH = 20


class VectorStore:
    """企业语义检索的单一入口。"""

    def __init__(self, collection_name: str | None = None, include_dupes: bool = False) -> None:
        collection_name = collection_name or settings.CHROMA_COLLECTION
        # 统一走策略工厂：本地 sentence-transformers 或 OpenAI embedding
        embeddings = create_embeddings()

        if settings.CHROMA_HOST:
            self._store = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                client_settings={"chroma_server_host": settings.CHROMA_HOST},
            )
        else:
            persist_dir = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)
            self._store = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=persist_dir,
            )

    async def add(self, texts: list[str], metadatas: list[dict] | None = None, ids: list[str] | None = None) -> None:
        self.add_texts(texts, metadatas, ids)

    def _add_batched(self, texts: list[str], metadatas: list[dict] | None, ids: list[str] | None) -> None:
        """按 _EMBED_BATCH 分批写入向量库，规避 embedding 供应商批量上限。"""
        n = len(texts)
        for start in range(0, n, _EMBED_BATCH):
            end = min(start + _EMBED_BATCH, n)
            self._store.add_texts(
                texts=texts[start:end],
                metadatas=metadatas[start:end] if metadatas else None,
                ids=ids[start:end] if ids else None,
            )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None, ids: list[str] | None = None) -> None:
        """同步写入（供 CLI 脚本等非异步场景使用）。"""
        self._add_batched(texts, metadatas, ids)

    async def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        return self.search_sync(query, top_k)

    def search_sync(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        """同步语义检索（供 Tool / CLI 使用）。"""
        top_k = top_k or settings.TOP_K_VECTOR_RETRIEVAL
        docs = self._store.similarity_search(query, k=top_k)
        return [
            {"content": d.page_content, "metadata": d.metadata}
            for d in docs
        ]

    async def delete(self, ids: list[str]) -> None:
        self._store.delete(ids=ids)

    # ---------- 集合管理（切换 embedding 模型后需重置向量库） ----------

    def list_collections(self) -> list[str]:
        """列出当前向量库中的所有集合。"""
        client = self._store._client
        return [c.name for c in client.list_collections()]

    def reset_collection(self, collection_name: str | None = None) -> None:
        """删除指定集合（默认当前配置的集合）。

        切换 embedding 供应商/模型后调用，避免旧向量维度不匹配。
        删除后，下次写入或检索时会自动重建同名集合。
        """
        name = collection_name or settings.CHROMA_COLLECTION
        client = self._store._client
        try:
            client.delete_collection(name)
            print(f"[ok] 已删除集合: {name}")
        except Exception as exc:  # 集合不存在等
            if "not found" in str(exc).lower() or "does not exist" in str(exc).lower():
                print(f"[skip] 集合不存在，无需清理: {name}")
            else:
                raise

    @property
    def store(self):
        return self._store


vector_store = VectorStore()