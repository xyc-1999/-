/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 说明：原先用 rewrites 代理 /api/:path* 到后端，但 rewrites 会命中 app/api 下的
  // Route Handler（尤其 /api/v1/chat 的 SSE 转发），并对其流式响应整体缓冲，导致
  // 逐字流式失效。现移除 rewrites，改为 app/api/[...path]/route.ts 通用代理转发普通
  // 请求；流式端点（/api/v1/chat）由更具体的 Route Handler 优先处理。
};

module.exports = nextConfig;