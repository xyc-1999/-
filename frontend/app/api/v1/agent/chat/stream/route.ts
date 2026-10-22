// 流式代理：绕过 next.config rewrites() 对 SSE 的缓冲，
// 手动将后端流 body 逐块管道返回给浏览器。
export const dynamic = "force-dynamic";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8900";

export async function POST(req: Request): Promise<Response> {
  // 透传前端 JSON body（session_id + message）
  const bodyText = await req.text();

  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND}/api/v1/agent/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: bodyText,
      // POST 也会被 Next 运行时缓冲；no-store 让流式 body 实时透传
      cache: "no-store",
    });
  } catch (err) {
    return new Response(`data: 后端连接失败：${String(err)}\n\n`, {
      status: 502,
      headers: { "Content-Type": "text/event-stream; charset=utf-8" },
    });
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      "X-Accel-Buffering": "no",
      Connection: "keep-alive",
    },
  });
}