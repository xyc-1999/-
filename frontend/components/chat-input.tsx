"use client";

import { useState } from "react";
import { ArrowUp, Paperclip, SendHorizonal } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (text: string) => void;
  onUpload?: (file: File) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  onUpload,
  disabled,
  placeholder = "输入你的问题，Enter 发送，Shift+Enter 换行…",
}: ChatInputProps) {
  const [text, setText] = useState("");

  function submit() {
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  }

  function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file && onUpload) onUpload(file);
    e.target.value = "";
  }

  return (
    <div className="animate-fade-in rounded-2xl border border-border/70 bg-card/80 p-2 shadow-xl shadow-black/20 backdrop-blur">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        rows={1}
        placeholder={placeholder}
        autoFocus
        className="min-h-[28px] w-full resize-none bg-transparent px-2 py-1 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
      />
      <div className="flex items-center justify-between pl-1">
        <label className="flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground">
          <Paperclip className="h-4 w-4" />
          知识库文档
          <input
            type="file"
            accept=".txt,.md,.markdown,.pdf"
            className="hidden"
            onChange={handleUpload}
            disabled={!onUpload}
          />
        </label>
        <button
          onClick={submit}
          disabled={!text.trim() || disabled}
          className={cn(
            "flex h-9 w-9 items-center justify-center rounded-xl transition-all",
            text.trim() && !disabled
              ? "bg-gradient-to-br from-primary to-accent text-background shadow-lg shadow-primary/30 hover:brightness-110"
              : "bg-muted text-muted-foreground"
          )}
          aria-label="发送"
        >
          {text.trim() ? <SendHorizonal className="h-4 w-4" /> : <ArrowUp className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}