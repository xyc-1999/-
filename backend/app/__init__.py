"""enterprise-agent-system 后端应用包。

分层架构：
- api        : FastAPI 路由 / 中间件
- agents     : LangChain / LangGraph 智能体定义
- core       : 配置、日志、安全
- db         : SQLAlchemy MySQL 模型 + Redis + 仓库层
- memory     : 会话记忆(Redis) 与 长期记忆/检索(Chroma)
- mcp        : MCP 客户端与协议适配
- services   : 领域服务编排
- schemas    : Pydantic 请求/响应模型
- utils      : 通用工具
"""