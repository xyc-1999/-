// SSE 流式代理：GET /api/v1/chat
// EventSource 仅支持 GET，参数经 query 传递。前端曾用 next.config.js 的 rewrites
// 代理 /api/:path*，但该代理会对 SSE 整体缓冲导致逐字流式失效；现已有更具体的
// 本 Route Handler 接管 /api/v1/chat（静态路由优先于通用代理），直接把后端流体逐
// 块透传回浏览器，绕开会缓冲的代理层。
export const dynamic = "force-dynamic";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8900";

export async function GET(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const qs = url.searchParams.toString();

  let upstream: Response;
  try {
    upstream = await fetch(`${BACKEND}/api/v1/chat?${qs}`, {
      method: "GET",
      headers: { Accept: "text/event-stream" },
      // 关键：Next.js 默认会对 GET fetch 做缓存/整体缓冲，导致 SSE 无法逐块
      // 流式透传。必须显式关闭缓存才能把上游流实时转发给浏览器。
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
    },
  });
}