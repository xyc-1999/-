"use client";

import { useState } from "react";
import { FilePlus2, Sparkles, TicketCheck } from "lucide-react";
import { useChat } from "@/hooks/use-chat";
import { Sidebar } from "@/components/sidebar";
import { AgentMessage } from "@/components/agent-message";
import { ChatInput } from "@/components/chat-input";
import { TicketDrawer } from "@/components/ticket-drawer";

export default function Home() {
  const chat = useChat();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [kbNotice, setKbNotice] = useState<string | null>(null);

  /** 上传知识库文档 */
  async function handleUpload(file: File) {
    setKbNotice(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("/api/v1/knowledge/upload", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || `HTTP ${res.status}`);
      setKbNotice(`文档已入库: ${data.message}`);
    } catch (err) {
      setKbNotice(`上传失败: ${String(err)}`);
    }
    setTimeout(() => setKbNotice(null), 5000);
  }

  return (
    <div className="app-bg flex h-screen w-screen overflow-hidden">
      {/* 左侧边栏 */}
      <Sidebar
        sessions={chat.sessions}
        health={chat.health}
        sortOrder={chat.sortOrder}
        onSortChange={chat.setSortOrder}
        onNewChat={chat.newChat}
        onSelectSession={chat.selectSession}
        onClearSession={chat.clearSession}
      />

      {/* 主聊天区 */}
      <main className="relative flex min-w-0 flex-1 flex-col">
        {/* 顶部栏 */}
        <header className="flex shrink-0 items-center justify-between border-b border-border/50 bg-card/30 px-5 py-3 backdrop-blur">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">对话</span>
            <span className="text-xs text-muted-foreground">{chat.activeSessionId}</span>
          </div>
          <button
            onClick={() => setDrawerOpen(true)}
            className="flex items-center gap-1.5 rounded-lg border border-border/70 px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground"
          >
            <TicketCheck className="h-4 w-4" />
            我的工单
          </button>
        </header>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex max-w-3xl flex-col gap-5">
            {chat.messages.length === 0 && (
              <div className="animate-fade-in mt-16 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/30 to-accent/30 text-primary shadow-xl shadow-primary/20">
                  <Sparkles className="h-8 w-8" />
                </div>
                <h2 className="text-xl font-semibold">你好，有什么可以帮你？</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  企业智能客服系统 · 接入知识库与工单服务
                </p>
              </div>
            )}

            {chat.messages.map((m, i) =>
              m.role === "user" ? (
                <UserBubble key={i} content={m.content} />
              ) : (
                <AgentMessage
                  key={i}
                  content={m.content}
                  thoughts={undefined}
                  streaming={m.streaming}
                />
              )
            )}

            {/* 上传提示 */}
            {kbNotice && (
              <div className="animate-fade-in flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-xs text-primary">
                <FilePlus2 className="h-3.5 w-3.5" />
                {kbNotice}
              </div>
            )}
          </div>
        </div>

        {/* 输入区 */}
        <div className="mx-auto w-full max-w-3xl shrink-0 px-4 pb-5">
          <ChatInput onSend={chat.send} onUpload={handleUpload} disabled={chat.streaming} />
        </div>
      </main>

      {/* 右侧工单抽屉 */}
      <TicketDrawer open={drawerOpen} onOpenChange={setDrawerOpen} />
    </div>
  );
}

function UserBubble({ content }: { content: string }) {
  return (
    <div className="animate-fade-in flex justify-end gap-3">
      <div className="max-w-[80%] rounded-2xl rounded-tr-sm border border-primary/30 bg-gradient-to-br from-primary/20 to-accent/10 px-4 py-2.5 text-sm leading-relaxed">
        {content}
      </div>
    </div>
  );
}