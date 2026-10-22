"use client";

import { Database, HardDrive, Layers } from "lucide-react";
import type { HealthResponse } from "@/types/chat";
import { cn } from "@/lib/utils";

interface StatusIndicatorsProps {
  health: HealthResponse | null;
}

const SERVICE_META = {
  mysql: { label: "MySQL", Icon: Database },
  redis: { label: "Redis", Icon: Layers },
  chroma: { label: "Chroma", Icon: HardDrive },
} as const;

/** 侧边栏底部的服务连接状态指示灯 */
export function StatusIndicators({ health }: StatusIndicatorsProps) {
  return (
    <div className="space-y-2 border-t border-border/60 pt-3">
      <div className="px-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        服务状态
      </div>
      {(Object.keys(SERVICE_META) as Array<keyof typeof SERVICE_META>).map((key) => {
        const { label, Icon } = SERVICE_META[key];
        const dep = health?.dependencies?.[key];
        const isOk = dep?.status === "ok";
        return (
          <div
            key={key}
            className="flex items-center justify-between rounded-md px-2 py-1.5 text-xs text-muted-foreground hover:bg-muted/40"
            title={dep?.error || label}
          >
            <span className="flex items-center gap-2">
              <Icon className="h-3.5 w-3.5" />
              {label}
            </span>
            <span
              className={cn(
                "flex items-center gap-1.5",
                dep?.status === "error" ? "text-destructive" : "text-success"
              )}
            >
              <span
                className={cn(
                  "h-2 w-2 rounded-full",
                  isOk ? "bg-success animate-glow" : "bg-destructive animate-pulse"
                )}
              />
              {isOk ? "在线" : "离线"}
            </span>
          </div>
        );
      })}
    </div>
  );
}