import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "智能客服助手 · Enterprise Agent",
  description: "AI 客服系统 - 对话 · 知识库 · 工单",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className="dark">
      <body>{children}</body>
    </html>
  );
}