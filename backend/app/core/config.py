"""应用核心配置。

集中管理所有环境变量，通过 pydantic-settings 从 .env 读取。
所有业务模块统一从这里取配置，禁止散落硬编码。
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置对象。"""

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),  # 支持根目录或 backend 目录下的 .env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 基础 ----------
    APP_NAME: str = "enterprise-agent-system"
    APP_ENV: str = Field(default="development", description="development|staging|production")
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8900
    LOG_LEVEL: str = "INFO"

    # ---------- LLM (DeepSeek：OpenAI 兼容协议) ----------
    # DeepSeek 官方不提供 embedding 接口，聊天走 OpenAI 兼容协议，
    # 向量嵌入由本地模型承担，见 EMBEDDING_PROVIDER。
    OPENAI_API_KEY: str = ""            # 兼容字段：通用 OpenAI 兼容 key
    DEEPSEEK_API_KEY: str = ""          # 推荐：显式填 DeepSeek key（优先于上方）
    OPENAI_BASE_URL: str = "https://api.deepseek.com/v1"
    # DeepSeek 聊天模型：deepseek-chat / deepseek-reasoner
    LLM_CHAT_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096

    @property
    def LLM_API_KEY(self) -> str:
        """返回生效的 API Key：DEEPSEEK_API_KEY 优先，兜底 OPENAI_API_KEY。"""
        return self.DEEPSEEK_API_KEY or self.OPENAI_API_KEY

    # ---------- Embedding (向量嵌入) ----------
    # DeepSeek 无 embedding 接口，向量检索由独立供应商承担。
    # 可选值：dashscope(默认) | openai | sentence_transformers
    EMBEDDING_PROVIDER: str = "dashscope"
    # Qwen 模型托管在阿里云 DashScope（OpenAI 兼容端点）
    EMBEDDING_API_KEY: str = ""    # DashScope(通义千问) 的 API Key
    EMBEDDING_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # 模型名：qwen3-text-embedding 系列，用户指定 qwen3.7-text-embedding-flash
    EMBEDDING_MODEL: str = "qwen3.7-text-embedding-flash"
    # --- 备选供应商 ---
    # openai:    需同时设置 EMBEDDING_API_KEY/EMBEDDING_BASE_URL 为 OpenAI 官方
    # sentence_transformers: 本地模型，离线可用；EMBEDDING_HF_MODEL 指定 HF 模型
    EMBEDDING_HF_MODEL: str = "BAAI/bge-m3"

    # ---------- MySQL ----------
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "enterprise_agent"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """拼装 SQLAlchemy 连接串（PyMySQL 驱动）。"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
        )

    # ---------- Redis ----------
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ---------- ChromaDB (向量库) ----------
    CHROMA_PERSIST_DIR: str = "./backend/data/chroma"
    CHROMA_COLLECTION: str = "enterprise_documents"
    CHROMA_HOST: str = ""  # 非空则走 chroma server 模式
    CHROMA_PORT: int = 8000
    # ---------- 知识库文档 ----------
    KB_DOCS_DIR: str = "./backend/data/documents"  # 入库源文档目录
    KB_CHUNK_SIZE: int = 500       # 分片大小（字符）
    KB_CHUNK_OVERLAP: int = 50     # 分片重叠

    # ---------- 会话 / 记忆 ----------
    SESSION_TTL_SECONDS: int = 86400 * 7  # 会话记忆默认保留 7 天
    MEMORY_WINDOW_MESSAGES: int = 20      # 短路记忆保留的最近消息数
    TOP_K_VECTOR_RETRIEVAL: int = 4       # 向量检索返回条数

    # ---------- 鉴权 ----------
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24h
    # 允许的 API Key / CORS 来源
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ---------- MCP ----------
    MCP_CONFIG_PATH: str = "./backend/mcp_servers/config.yaml"


@lru_cache
def get_settings() -> Settings:
    """返回全局单例配置。"""
    return Settings()


settings = get_settings()