"""Redis 会话记忆实现。

使用 Redis List 存储每个 session 的近期消息，
并计算 message-id 映射用于短期记忆窗口与续接。
"""
import json
import time
from typing import Any

from app.core.config import settings
from app.db.redis import redis_client


class RedisSessionMemory:
    """基于 Redis List 的滚动会话记忆。"""

    _KEY_PREFIX = "agent:mem"
    _LAST_PREFIX = "agent:last"

    def _key(self, session_id: str) -> str:
        return f"{self._KEY_PREFIX}:{session_id}"

    def _last_key(self, session_id: str) -> str:
        return f"{self._LAST_PREFIX}:{session_id}"

    async def add_message(self, session_id: str, role: str, content: str, meta: dict | None = None) -> None:
        """追加一条消息到会话记忆。"""
        payload = json.dumps({"role": role, "content": content, "meta": meta or {}}, ensure_ascii=False)
        key = self._key(session_id)
        redis_client.rpush(key, payload)
        # 限制记忆窗口长度，防止无限增长
        redis_client.ltrim(key, -settings.MEMORY_WINDOW_MESSAGES, -1)
        redis_client.expire(key, settings.SESSION_TTL_SECONDS)
        # 记录最后活跃时间戳（毫秒），用于按时间排序
        redis_client.set(self._last_key(session_id), int(time.time() * 1000))
        redis_client.expire(self._last_key(session_id), settings.SESSION_TTL_SECONDS)

    async def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        """取出该会话的全部记忆消息（按时间正序）。"""
        items = redis_client.lrange(self._key(session_id), 0, -1)
        return [json.loads(i) for i in items]

    async def clear(self, session_id: str) -> None:
        redis_client.delete(self._key(session_id))
        redis_client.delete(self._last_key(session_id))

    async def build_chat_history(self, session_id: str) -> list[dict[str, str]]:
        """转换为 LangChain 所需的 (role, content) 历史。"""
        raw = await self.get_messages(session_id)
        # 仅保留 LangChain 支持的角色
        return [
            {"role": m["role"], "content": m["content"]}
            for m in raw
            if m["role"] in ("user", "assistant", "system", "tool")
        ]

    async def list_sessions(self, sort: str = "recent") -> list[dict[str, Any]]:
        """枚举全部会话索引：id、标题、消息数、创建/最后活跃时间。

        sort 支持: recent(最后活跃倒序) / oldest(最早创建) / messages(消息数倒序)。
        用 SCAN 遍历，避免 KEYS 阻塞。
        """
        sessions: dict[str, dict[str, Any]] = {}
        prefix = f"{self._KEY_PREFIX}:"
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=f"{prefix}*", count=200)
            for key in keys:
                k = key.decode("utf-8") if isinstance(key, bytes) else key
                session_id = k[len(prefix):]
                if not session_id:
                    continue
                try:
                    msgs = await self.get_messages(session_id)
                except Exception:  # noqa: BLE001
                    continue
                title = ""
                for m in msgs:
                    if m["role"] == "user" and m["content"]:
                        title = m["content"]
                        if len(title) > 14:
                            title = title[:14] + "…"
                        break
                last_raw = redis_client.get(self._last_key(session_id))
                last_ms = int(last_raw) if last_raw else self._created_ms(msgs)
                sessions[session_id] = {
                    "id": session_id,
                    "title": title or "新对话",
                    "message_count": len(msgs),
                    "updated_at": self._fmt_time(last_ms),
                }
            if cursor == 0:
                break

        items = list(sessions.values())
        if sort == "oldest":
            items.sort(key=lambda s: (s.get("updated_at") or "") or "")
        elif sort == "messages":
            items.sort(key=lambda s: s.get("message_count", 0), reverse=True)
        else:  # recent 默认
            items.sort(key=lambda s: (s.get("updated_at") or "-" * 24), reverse=True)
        return items

    @staticmethod
    def _fmt_time(ms: int | None) -> str | None:
        if not ms:
            return None
        try:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ms / 1000))
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _created_ms(msgs: list[dict[str, Any]]) -> int | None:
        """推断会话时间：优先取消息 meta 里的 ts，否则用当前时间回退。"""
        for m in reversed(msgs):
            meta = m.get("meta") or {}
            ts = meta.get("ts") or meta.get("created_at")
            if ts:
                return int(ts)
        return None


session_memory = RedisSessionMemory()