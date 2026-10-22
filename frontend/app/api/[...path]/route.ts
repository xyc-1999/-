// 通用 API 代理：把 /api/:path* 统一转发到后端。
// 说明：原先用 next.config.js 的 rewrites 代理 /api/:path*，但 rewrites 会命中并
// 覆盖 app/api 下的 Route Handler（如 /api/v1/chat 的 SSE 转发），且其代理会对 SSE
// 整体缓冲。改为：移除 rewrites，本文件作为通用代理处理普通 JSON 请求；
// 更具体的 Route Handler（v1/chat）优先匹配，从而保证流式不被缓冲。
export const dynamic = "force-dynamic";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8900";

async function proxy(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const backendUrl = `${BACKEND}${url.pathname}${url.search ? url.search : ""}`;

  const headers = new Headers(req.headers);
  // 移除与代理无关的请求头，避免陷阱头导致后端 4xx
  headers.delete("host");
  headers.delete("connection");

  // 统一定价 body 为 ArrayBuffer；空 body 置 null，避免把空流传给上游 fetch 导致 500
  let body: BodyInit | null = null;
  try {
    const buf = await req.arrayBuffer();
    if (buf.byteLength > 0) body = buf;
  } catch {
    body = null;
  }
  // 由 fetch 依据 Buffer 内容重算 Content-Length，删除原长度头防止错位
  headers.delete("content-length");

  const upstream = await fetch(backendUrl, {
    method: req.method,
    headers,
    body,
  });

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      ...(upstream.headers.get("content-type")
        ? { "Content-Type": upstream.headers.get("content-type")! }
        : {}),
    },
  });
}

export async function GET(req: Request) {
  return proxy(req);
}

export async function POST(req: Request) {
  return proxy(req);
}

export async function PUT(req: Request) {
  return proxy(req);
}

export async function PATCH(req: Request) {
  return proxy(req);
}

export async function DELETE(req: Request) {
  return proxy(req);
}

export async function OPTIONS(req: Request) {
  return proxy(req);
}