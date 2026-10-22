"use client";

import { useEffect, useState } from "react";
import { Ticket as TicketIcon } from "lucide-react";
import type { Ticket } from "@/types/chat";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface TicketDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const PRIORITY_META: Record<string, { label: string; className: string }> = {
  low: { label: "低", className: "bg-muted text-muted-foreground" },
  normal: { label: "普通", className: "bg-primary/20 text-primary" },
  high: { label: "高", className: "bg-warning/20 text-warning" },
  urgent: { label: "紧急", className: "bg-destructive/20 text-destructive" },
};

const STATUS_META: Record<string, { label: string; dot: string }> = {
  open: { label: "待处理", dot: "bg-warning" },
  processing: { label: "处理中", dot: "bg-primary" },
  resolved: { label: "已解决", dot: "bg-success" },
  closed: { label: "已关闭", dot: "bg-muted-foreground" },
};

export function TicketDrawer({ open, onOpenChange }: TicketDrawerProps) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch("/api/v1/tickets");
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
        setTickets(data.tickets || []);
      } catch (err) {
        setError(String(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent side="right" className="[&>button]:top-5">
        <DialogHeader className="border-b border-border/60 px-5 pb-4 pt-5">
          <DialogTitle className="flex items-center gap-2 text-base">
            <TicketIcon className="h-4 w-4 text-primary" />
            我的工单
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            来自 MySQL 的最近工单记录
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {loading && (
            <div className="py-10 text-center text-sm text-muted-foreground">加载中…</div>
          )}
          {error && (
            <div className="py-10 text-center text-sm text-destructive">{error}</div>
          )}
          {!loading && !error && tickets.length === 0 && (
            <div className="py-10 text-center text-sm text-muted-foreground">暂无工单</div>
          )}
          {!loading &&
            tickets.map((t) => {
              const p = PRIORITY_META[t.priority] ?? PRIORITY_META.normal;
              const s = STATUS_META[t.status] ?? STATUS_META.open;
              return (
                <div
                  key={t.id}
                  className="animate-fade-in space-y-2 rounded-xl border border-border/60 bg-card/70 p-3.5 transition-colors hover:border-primary/40"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className={cn("rounded-md px-1.5 py-0.5 text-[10px] font-medium", p.className)}>
                        {p.label}
                      </span>
                      <span className="flex items-center gap-1 text-[10px] text-muted-foreground">
                        <span className={cn("h-1.5 w-1.5 rounded-full", s.dot)} />
                        {s.label}
                      </span>
                    </div>
                    <span className="text-[10px] text-muted-foreground">
                      #{t.id} · {t.created_at?.slice(0, 10)}
                    </span>
                  </div>
                  <div className="text-sm font-medium text-foreground">{t.subject}</div>
                  <p className="line-clamp-3 text-xs leading-relaxed text-muted-foreground">
                    {t.content}
                  </p>
                </div>
              );
            })}
        </div>
      </DialogContent>
    </Dialog>
  );
}