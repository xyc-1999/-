"""MCP 客户端：与 FastMCP 服务器交互并获取工具列表。

企业可用它把遗留系统（数据库、ERP、IM）以标准 MCP 协议接入 Agent。
"""
import asyncio
from typing import Any

import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import settings


class MCPClient:
    """管理一组已注册的 MCP 服务器。"""

    def __init__(self, config_path: str | None = None) -> None:
        self._config = self._load_config(config_path)
        self._sessions: dict[str, ClientSession] = {}

    def _load_config(self, config_path: str | None) -> dict[str, Any]:
        path = config_path or settings.MCP_CONFIG_PATH
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {"servers": {}}

    def list_servers(self) -> list[str]:
        return list((self._config.get("servers") or {}).keys())

    async def connect(self, name: str) -> None:
        """启动一个 stdio MCP 服务器并建立会话。"""
        server = self._config["servers"][name]
        params = StdioServerParameters(command=server["command"], args=server.get("args", []))
        ctx = stdio_client(params)
        read, write = await ctx.__aenter__()
        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()
        self._sessions[name] = session

    async def get_tools(self, name: str) -> list[dict[str, Any]]:
        if name not in self._sessions:
            await self.connect(name)
        result = await self._sessions[name].list_tools()
        return [t.model_dump() for t in result.tools]

    async def call_tool(self, name: str, tool_name: str, arguments: dict) -> Any:
        if name not in self._sessions:
            await self.connect(name)
        result = await self._sessions[name].call_tool(tool_name, arguments)
        return result


async def main() -> None:
    client = MCPClient()
    print("registered servers:", client.list_servers())


if __name__ == "__main__":
    asyncio.run(main())