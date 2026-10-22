/** 对话消息类型 */
export type ChatRole = "user" | "assistant" | "system" | "tool";

export interface ThoughtStep {
  /** 调用的工具名称 */
  name: string;
  /** 工具入参 */
  args: Record<string, unknown>;
}

export interface ChatMessage {
  role: ChatRole;
  content: string;
  /** Agent 中间思考过程（调用的工具 + 入参） */
  thoughts?: ThoughtStep[];
  streaming?: boolean;
  createdAt?: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  agent_id?: number;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  usage?: Record<string, unknown>;
}

export interface ServiceStatus {
  status: "ok" | "error" | "degraded";
  error: string | null;
}

export interface HealthResponse {
  status: string;
  app: string;
  env: string;
  dependencies: {
    mysql: ServiceStatus;
    redis: ServiceStatus;
    chroma: ServiceStatus;
  };
}

export type TicketPriority = "low" | "normal" | "high" | "urgent";
export type TicketStatus = "open" | "processing" | "resolved" | "closed";

export interface Ticket {
  id: number;
  user_id: string;
  subject: string;
  content: string | null;
  priority: TicketPriority;
  status: TicketStatus;
  created_at: string | null;
  updated_at: string | null;
}

export interface TicketListResponse {
  user_id: string;
  total: number;
  tickets: Ticket[];
}