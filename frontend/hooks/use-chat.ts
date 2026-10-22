"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessage, HealthResponse } from "@/types/chat";
import { deleteSession, getSessionList, getSessionMessages } from "@/lib/api";

/**
 * 客服对话核心 Hook：
 *  - 管理消息列表 / 会话列表 / 流式状态
 *  - 用 EventSource 接入 GET /api/v1/chat 实现打字机效果
 *  - 轮询后端 /health 更新服务状态灯
 *  - 切换会话时拉取历史消息并回放
 */
export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<Array<{ id: string; title: string; active?: boolean }>>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>("main");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [sortOrder, setSortOrder] = useState<"recent" | "oldest" | "messages">("recent");
  const sessionCounter = useRef(0);
  const loadingSessionRef = useRef(false);

  // EventSource 引用：发送时创建，完成时关闭
  const esRef = useRef<EventSource | null>(null);

  /** 轮询后端健康状态 */
  const refreshHealth = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/health");
      if (res.ok) setHealth((await res.json()) as HealthResponse);
    } catch {
      /* 忽略，保持上次状态 */
    }
  }, []);

  useEffect(() => {
    refreshHealth();
    const timer = setInterval(refreshHealth, 10000);
    return () => clearInterval(timer);
  }, [refreshHealth]);

  /** 按 sort 拉取会话列表（覆盖式，保留当前活跃会话） */
  const refreshSessions = useCallback(async (sort: "recent" | "oldest" | "messages") => {
    try {
      const list = await getSessionList(sort);
      // 依据后端已存在会话的 chat-N id 恢复本地计数器，
      // 避免刷新后新会话继续用 chat-1/chat-2，与已有会话 id 冲突。
      let maxN = 0;
      for (const s of list) {
        const m = /^chat-(\d+)$/.exec(s.id);
        if (m) maxN = Math.max(maxN, parseInt(m[1], 10));
      }
      if (maxN > sessionCounter.current) sessionCounter.current = maxN;
      setSessions((prev) => {
        const active = prev.find((s) => s.active);
        const mapped = list.map((s) => ({
          id: s.id,
          title: s.title,
          active: active ? s.id === active.id : false,
        }));
        // 合并本地新增的活跃会话（避免被后端覆盖丢失）
        if (active && !list.some((s) => s.id === active.id)) {
          return [{ ...active }, ...mapped];
        }
        return mapped;
      });
    } catch {
      /* 保留现状 */
    }
  }, []);

  useEffect(() => {
    refreshSessions(sortOrder);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortOrder]);

  /** 新建会话 */
  const newChat = useCallback(() => {
    const id = `chat-${++sessionCounter.current}`;
    setActiveSessionId(id);
    setMessages([]);
    setSessions((prev) => [
      { id, title: "新对话", active: true },
      ...prev.map((s) => ({ ...s, active: false })),
    ]);
  }, []);

  /** 选择会话：从后端拉取历史消息并回放 */
  const selectSession = useCallback(
    async (id: string) => {
      if (loadingSessionRef.current) return;
      loadingSessionRef.current = true;
      setActiveSessionId(id);
      setSessions((prev) => prev.map((s) => ({ ...s, active: s.id === id })));
      // 立即清空视图，避免展示旧会话内容
      setMessages([]);
      try {
        const msgs = await getSessionMessages(id);
        setMessages(msgs);
      } catch {
        setMessages([]);
      } finally {
        loadingSessionRef.current = false;
      }
    },
    []
  );

  /** 删除会话：先同步删除后端记录，再更新本地状态，确保刷新后不再出现 */
  const clearSession = useCallback(
    async (id: string) => {
      // 无论后端成功与否都移除本地项，保持响应即时；后端失败则记录
      try {
        await deleteSession(id);
      } catch (err) {
        console.error("删除会话失败：", err);
      }
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (activeSessionId === id) {
        setMessages([]);
        setActiveSessionId("main");
        setSessions((prev) => prev.map((s) => ({ ...s, active: s.id === "main" })));
      }
    },
    [activeSessionId]
  );

  /** 流式切换的回调刷新 */
  function patchLastStreaming(streamingFlag: boolean) {
    setMessages((prev) => {
      const copy = [...prev];
      const last = copy[copy.length - 1];
      if (last && last.role === "assistant") copy[copy.length - 1] = { ...last, streaming: streamingFlag };
      return copy;
    });
  }

  /** 追加 token 到最后一条 assistant 消息 */
  function appendToken(token: string) {
    setMessages((prev) => {
      const copy = [...prev];
      const idx = copy.length - 1;
      if (idx < 0) return copy;
      const last = copy[idx];
      copy[idx] = { ...last, content: last.content + token };
      return copy;
    });
  }

  /** 发送消息（EventSource 流式） */
  const send = useCallback(
    (text: string) => {
      if (!text.trim() || streaming) return;

      // 追加用户与空助手消息
      setMessages((prev) => [
        ...prev,
        { role: "user", content: text },
        { role: "assistant", content: "", streaming: true },
      ]);
      setStreaming(true);

      // 将会话登记到侧边栏（若无则新增，标题取首条用户消息摘要）
      const title = text.length > 14 ? text.slice(0, 14) + "…" : text;
      const sid = activeSessionId;
      setSessions((prev) => {
        const exists = prev.some((s) => s.id === sid);
        if (exists) {
          return prev.map((s) => ({ ...s, active: s.id === sid }));
        }
        // 标题取首条用户消息摘要；仅当与其他会话重名时追加会话序号以区分
        const conflicted = prev.some((s) => s.title === title);
        const finalTitle = conflicted ? `${title}-${sid.replace("chat-", "")}` : title;
        return [
          { id: sid, title: finalTitle, active: true },
          ...prev.map((s) => ({ ...s, active: false })),
        ];
      });

      const query = new URLSearchParams({ session_id: activeSessionId, message: text.trim() });
      const es = new EventSource(`/api/v1/chat?${query.toString()}`);

      es.onmessage = (event) => {
        const data = event.data;
        if (data === "[DONE]") return;
        appendToken(data);
      };

      es.onerror = () => {
        // 后端结束会触发 error，关闭连接
        es.close();
        esRef.current = null;
        patchLastStreaming(false);
        setStreaming(false);
      };

      esRef.current = es;
    },
    [activeSessionId, streaming]
  );

  return {
    messages,
    sessions,
    health,
    streaming,
    sortOrder,
    setSortOrder,
    activeSessionId,
    send,
    newChat,
    selectSession,
    clearSession,
  };
}