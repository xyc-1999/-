"""FastMCP 示例服务器——企业数据库助手。

运行方式（在 backend 目录）：
    python -m mcp_servers.core.database_server
"""
from fastmcp import FastMCP

# 指定服务器名，便于 MCP 客户端识别
mcp = FastMCP("database-assist")

# 表结构缓存（演示用，可替换为真实 MySQL 查询）
_TABLES = {
    "agents": ("id", "name", "description", "state", "created_at"),
    "session_records": ("id", "session_id", "role", "content", "created_at"),
}


@mcp.tool()
def list_tables() -> list[str]:
    """列出当前业务数据库中的所有表。"""
    return list(_TABLES.keys())


@mcp.tool()
def describe_table(table: str) -> list[str]:
    """返回指定表的字段列表。

    Args:
        table: 表名，如 agents。
    """
    if table not in _TABLES:
        raise ValueError(f"未知表: {table}")
    return list(_TABLES[table])


@mcp.tool()
def inspect_schema() -> str:
    """快速返回完整表结构概览，用于辅助业务问答。"""
    return "\n".join(f"{t}: {cols}" for t, cols in _TABLES.items())


if __name__ == "__main__":
    mcp.run()  # 默认 STDIO 传输