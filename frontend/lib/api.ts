import type { ChatMessage, ChatRequest, ChatResponse } from "@/types/chat";

/** 后端 API 前端封装。所有请求会经过 next.config.js 的 rewrites 代理。 */
export async function postChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch("/api/v1/agent/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<ChatResponse>;
}

/** 获取某会话的历史消息（用于回放）。返回按时间正序的消息数组。 */
export async function getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
  const res = await fetch(`/api/v1/session/${encodeURIComponent(sessionId)}/messages`);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  const data = (await res.json()) as {
    session_id: string;
    messages?: Array<{ role: string; content: string }>;
  };
  return (data.messages || []).map((m) => ({
    role: m.role as ChatMessage["role"],
    content: m.content,
  }));
}

export interface SessionSummary {
  id: string;
  title: string;
  message_count: number;
  updated_at: string | null;
}

/** 拉取后端会话索引。sort: recent|oldest|messages */
export async function getSessionList(
  sort: "recent" | "oldest" | "messages" = "recent"
): Promise<SessionSummary[]> {
  const res = await fetch(`/api/v1/session?sort=${sort}`);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  const data = (await res.json()) as {
    total: number;
    sessions?: SessionSummary[];
  };
  return data.sessions || [];
}

/** 删除后端会话（会同步清除其 Redis 记录，刷新后不再出现）。 */
export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`/api/v1/session/${encodeURIComponent(sessionId)}/clear`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
}