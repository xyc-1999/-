"""健康检查路由：整体状态 + 依赖组件分项探活(MySQL/Redis/Chroma)。"""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


def _check_mysql() -> tuple[str, str | None]:
    try:
        from sqlalchemy import text
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok", None
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


def _check_redis() -> tuple[str, str | None]:
    try:
        from app.db.redis import redis_client

        redis_client.ping()
        return "ok", None
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


def _check_chroma() -> tuple[str, str | None]:
    try:
        from app.memory.chroma_store import VectorStore

        VectorStore().list_collections()
        return "ok", None
    except Exception as exc:  # noqa: BLE001
        return "error", str(exc)


@router.get("/health")
async def health() -> dict:
    mysql, mysql_err = _check_mysql()
    redis, redis_err = _check_redis()
    chroma, chroma_err = _check_chroma()

    overall = "ok" if all(s == "ok" for s in (mysql, redis, chroma)) else "degraded"
    return {
        "status": overall,
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "dependencies": {
            "mysql": {"status": mysql, "error": mysql_err},
            "redis": {"status": redis, "error": redis_err},
            "chroma": {"status": chroma, "error": chroma_err},
        },
    }