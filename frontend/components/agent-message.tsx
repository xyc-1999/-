"use client";

import { Bot, Wrench } from "lucide-react";
import type { ThoughtStep } from "@/types/chat";
import { cn } from "@/lib/utils";
import { Markdown } from "@/components/markdown";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface AgentMessageProps {
  content: string;
  thoughts?: ThoughtStep[];
  streaming?: boolean;
}

/** Agent 消息气泡：Markdown 渲染 + 流式光标 + 可折叠的思考过程(工具调用) */
export function AgentMessage({ content, thoughts = [], streaming }: AgentMessageProps) {
  return (
    <div className="group animate-fade-in flex gap-3">
      {/* 头像 */}
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary/80 to-accent text-background shadow-lg shadow-primary/20">
        <Bot className="h-4.5 w-4.5" />
      </div>

      <div className="min-w-0 flex-1 space-y-2">
        {/* 思考过程：可折叠的 Agent 推理步骤 */}
        {thoughts.length > 0 && (
          <div className="rounded-lg border border-border/60 bg-muted/40 px-3 py-1.5">
            <Accordion type="single" collapsible>
              <AccordionItem value="thoughts" className="border-0">
                <AccordionTrigger>
                  <span className="flex items-center gap-1.5">
                    <Wrench className="h-3.5 w-3.5 text-primary" />
                    已调用 {thoughts.length} 个工具
                  </span>
                </AccordionTrigger>
                <AccordionContent>
                  <ul className="mt-1 space-y-2">
                    {thoughts.map((t, i) => (
                      <li key={i} className="rounded-md border border-border/50 bg-card/80 p-2">
                        <div className="mb-1 flex items-center gap-1.5 text-xs font-medium">
                          <span className="text-primary">→</span>
                          <span className="mono font-mono">{t.name}</span>
                        </div>
                        <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-md bg-black/30 p-1.5 font-mono text-[11px] leading-relaxed text-muted-foreground">
                          {JSON.stringify(t.args, null, 2)}
                        </pre>
                      </li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        )}

        {/* 气泡 */}
        <div className="rounded-2xl rounded-tl-sm border border-border/60 bg-card px-4 py-3 text-sm shadow-sm">
          {streaming ? (
            <div className="stream-caret">
              <Markdown content={content} />
            </div>
          ) : content ? (
            <Markdown content={content} />
          ) : (
            <div className="text-muted-foreground">正在思考…</div>
          )}
        </div>
      </div>
    </div>
  );
}