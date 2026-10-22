"use client";

import { MessageSquare, Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { StatusIndicators } from "@/components/status-indicators";
import type { HealthResponse } from "@/types/chat";

export interface SessionItem {
  id: string;
  title: string;
  active?: boolean;
}

interface SidebarProps {
  sessions: SessionItem[];
  health: HealthResponse | null;
  sortOrder: "recent" | "oldest" | "messages";
  onSortChange: (sort: "recent" | "oldest" | "messages") => void;
  onNewChat: () => void;
  onSelectSession: (id: string) => void;
  onClearSession: (id: string) => void;
}

const SORT_OPTIONS = [
  { value: "recent", label: "最近活跃" },
  { value: "oldest", label: "最早创建" },
  { value: "messages", label: "消息最多" },
] as const;

export function Sidebar({
  sessions,
  health,
  sortOrder,
  onSortChange,
  onNewChat,
  onSelectSession,
  onClearSession,
}: SidebarProps) {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-border/50 bg-card/40 backdrop-blur">
      {/* 品牌区 */}
      <div className="flex items-center gap-2 border-b border-border/50 px-4 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-sm font-bold text-background shadow-lg shadow-primary/30">
          AI
        </div>
        <div>
          <div className="text-sm font-semibold">智能客服助手</div>
          <div className="text-[11px] text-muted-foreground">Enterprise Agent</div>
        </div>
      </div>

      {/* 新建对话 */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl border border-primary/30 bg-primary/10 py-2.5 text-sm font-medium text-primary transition-all hover:border-primary/60 hover:bg-primary/20"
        >
          <Plus className="h-4 w-4" />
          新建对话
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto px-3 pb-2">
        <div className="px-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          历史会话
        </div>
        <div className="mb-1 flex items-center justify-between px-1">
          <label htmlFor="session-sort" className="text-[10px] text-muted-foreground/70">排序</label>
          <select
            id="session-sort"
            value={sortOrder}
            onChange={(e) => onSortChange(e.target.value as "recent" | "oldest" | "messages")}
            className="rounded-md border border-border/50 bg-muted/40 px-1.5 py-0.5 text-[11px] text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => onSelectSession(s.id)}
              className={cn(
                "group flex cursor-pointer items-center justify-between rounded-lg px-2.5 py-2 text-sm transition-colors",
                s.active
                  ? "bg-primary/15 text-foreground"
                  : "text-muted-foreground hover:bg-muted/40 hover:text-foreground"
              )}
            >
              <span className="flex min-w-0 items-center gap-2">
                <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{s.title}</span>
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onClearSession(s.id);
                }}
                className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100 hover:text-destructive"
                aria-label="删除会话"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 服务状态 */}
      <div className="p-3">
        <StatusIndicators health={health} />
      </div>
    </aside>
  );
}