# enterprise-agent-system

基于 **LangChain + LangGraph + FastMCP** 的企业级 AI Agent 系统。提供可扩展的智能体编排框架，内置会话记忆（Redis）、企业知识库语义检索（ChromaDB）、业务数据持久化（MySQL），并提供统一的 FastAPI 网关与 Next.js 前端。

**技术栈速览**

| 层 | 技术 |
| --- | --- |
| 后端 | Python 3.11/3.12（镜像用 3.11）, FastAPI, LangChain, LangGraph, FastMCP |
| 数据 | MySQL 8.0（业务）, Redis 7.0（会话/缓存）, ChromaDB（向量库）|
| 前端 | Next.js 14 (App Router), Tailwind CSS, Shadcn UI |
| 编排 | Docker Compose 一键启动中间件 |

---

## 目录结构

```
enterprise-agent-system/
├── backend/                     # Python 后端
│   ├── app/                     # 应用包
│   │   ├── api/                 #   FastAPI 路由 & 中间件
│   │   │   ├── routes/          #     agent / chat_events / session / knowledge / tickets / health
│   │   │   └── middleware/      #     鉴权/限流扩展位
│   │   ├── agents/              #   LangChain / LangGraph 智能体
│   │   │   ├── base.py          #     LLM 工厂 & 嵌入工厂（OpenAI 兼容）
│   │   │   ├── graph.py         #     LangGraph 状态图
│   │   │   ├── tools.py         #     工具集合
│   │   │   └── nodes/           #     图节点实现
│   │   ├── core/                #   配置(config) / 日志 / 安全
│   │   ├── db/                  #   SQLAlchemy 引擎 & 模型 & 仓库层
│   │   ├── memory/              #   会话记忆(redis_memory) + 向量检索(chroma_store)
│   │   ├── mcp/                 #   MCP 客户端（接入外部工具服务器）
│   │   ├── schemas/             #   Pydantic 请求/响应
│   │   ├── services/            #   领域服务编排（含知识库 kb_service）
│   │   └── utils/
│   ├── mcp_servers/             # 内置 MCP 服务器（FastMCP）
│   ├── sql/init.sql             # 数据库初始化脚本（表结构与种子数据）
│   ├── data/                    # 运行时数据（documents 源文档 / chroma 向量库）
│   ├── scripts/
│   │   ├── init_db.py           #   初始化数据库结构
│   │   ├── ingest_kb.py         #   知识库文档入库
│   │   └── reset_chroma.py      #   向量库运维（列出 / 重置集合）
│   ├── requirements.txt         # 完整依赖（含测试/可选包，基于 Python 3.11）
│   ├── requirements-core.txt    # 运行时最小依赖（pypdf + pymupdf 用于 PDF 解析）
│   └── tests/                   # 单元 & 集成测试
├── frontend/                    # Next.js 14 前端
│   ├── app/                     #   App Router 页面与路由
│   │   ├── page.tsx             #     主界面（聊天/侧边栏/工单抽屉）
│   │   └── api/                 #     Route Handler：通用代理 [...path] + 流式 SSE 转发
│   │       ├── [...path]/route.ts           #   普通 JSON API 代理 → 后端
│   │       └── v1/chat/route.ts             #   SSE 流式 GET 转发（cache:no-store）
│   ├── components/              #   布局组件（sidebar / chat 区等）
│   │   └── ui/                  #   Shadcn UI 组件
│   ├── hooks/use-chat.ts        #   对话核心逻辑（流式/会话/排序/删除）
│   ├── lib/                     #   API 封装 & cn 工具
│   └── types/                   #   TS 类型
├── docker-compose.yml           # MySQL + Redis 编排
├── .env.example                 # 环境变量模板
└── README.md
```

---

## 快速开始

### 1) 环境要求
- Docker & Docker Compose（推荐）
- Python 3.11 / 3.12（本机直接运行时；3.13+ 请用 Docker）
- Node.js 18+（前端）

### 2) 配置环境变量
复制模板并填入真实密钥：
```bash
# PowerShell (Windows)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```
重点修改 `DEEPSEEK_API_KEY`（模型即 DeepSeek，无需改其他配置）。

### 3) 启动基础设施（MySQL + Redis）
```bash
docker compose up -d
docker compose ps
```
- MySQL: 首次启动自动执行 `backend/sql/init.sql`，创建库 `enterprise_agent` 及表结构。
- Redis: AOF 持久化已开启，端口默认映射到主机 3306/6379。
- 停止（删除数据卷）：`docker compose down -v`

### 4) 启动后端

**方式 A：Docker（推荐，规避本机 Python 环境差异）**

后端镜像基于 `python:3.11-slim`，可解决本机 Python 3.13 下 `chromadb` 无预编译 wheel 导致的编译问题：
```bash
# 构建镜像
docker build -t enterprise-agent-backend ./backend

# 启动（--env-file 注入 .env；挂载数据目录以持久化向量库）
docker run -d --name enterprise-agent-backend \
  --network agent-net --env-file .env \
  -p 8900:8900 \
  -v "${PWD}\backend\data:/code/data" \
  enterprise-agent-backend

docker logs -f enterprise-agent-backend
```

**方式 B：本机 Python 虚拟环境（需 Python 3.11/3.12）**
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1   Linux: source .venv/bin/activate
# 推荐仅装运行时核心依赖（不含 torch 等可选包）
pip install -r requirements-core.txt
# 若需完整依赖含测试/可选能力，改用: pip install -r requirements.txt

# 若未用 SQL 自动建表，先初始化数据结构
python -m scripts.init_db

# 启动服务
uvicorn app.main:app --reload --port 8900
```
> **注意**：`chromadb 0.5.x` 仅在 Python 3.11/3.12 提供预编译 wheel。若本机是 **Python 3.13+**，直接 `pip install` 会尝试从源码编译 `chroma-hnswlib`（C++）而失败，请使用方式 A（Docker）。

Swagger 文档： http://localhost:8900/docs

### 5) 启动前端
```bash
cd frontend
npm install
cp .env.example .env.local   # 可选，默认代理到 :8900
npm run dev
```
访问 http://localhost:3000

> **前端能力**：逐字流式打字机回复、Markdown 渲染 + 代码高亮、Agent 思考过程折叠面板、左侧历史会话（按时间/活跃度排序、支持单个删除并持久）、右侧「我的工单」抽屉、深色科技主题，以及底部三服务健康状态灯（MySQL / Redis / Chroma）。

---

## 后端设计

### LLM 接入（DeepSeek，`.env` 关键项）
```ini
DEEPSEEK_API_KEY=sk-xxx        # DeepSeek 官网平台申请
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_CHAT_MODEL=deepseek-chat   # 或 deepseek-reasoner
```
聊天模型走 **OpenAI 兼容协议**，`OPENAI_BASE_URL` 指向 DeepSeek 即可，无需改动代码即可切换模型名。

> **架构注意**：DeepSeek **不提供 embedding 接口**，向量检索（ChromaDB）默认改用**通义千问 Qwen** 嵌入模型 `qwen3.7-text-embedding-flash`（托管于阿里云 DashScope，OpenAI 兼容协议）。如需换回 OpenAI 或本地模型，切换 `EMBEDDING_PROVIDER` 即可。

| Embedding | 配置 |
| --- | --- |
| DashScope（默认） | `EMBEDDING_PROVIDER=dashscope`，`EMBEDDING_API_KEY=xxx`，`EMBEDDING_MODEL=qwen3.7-text-embedding-flash` |
| OpenAI | `EMBEDDING_PROVIDER=openai`，`EMBEDDING_API_KEY=xxx`，`EMBEDDING_BASE_URL=https://api.openai.com/v1` |
| 本地 | `EMBEDDING_PROVIDER=sentence_transformers`，`EMBEDDING_HF_MODEL=BAAI/bge-m3` |

聊天与嵌入分属两套密钥互不干扰：聊天用 `DEEPSEEK_API_KEY`，嵌入用 `EMBEDDING_API_KEY`。`create_embeddings()`（`app/agents/base.py`）按 `EMBEDDING_PROVIDER` 返回不同实现的嵌入模型，调用方无需关心底层差异。

### requirements-core.txt（运行时最小依赖）

`requirements-core.txt` 只含启动后端所需的核心包，**不含** `torch`/`sentence-transformers`（仅本地 embedding 备用）等可选重依赖，因此：
- 安装体积小、速度快；
- 避免 Python 3.13 下编译 `chroma-hnswlib` 失败；
- 适合容器镜像与生产部署。

> PDF 解析必需依赖 `pypdf` 与 `pymupdf` 已包含在 `requirements-core.txt` 中：`pypdf` 提取文本型 PDF，`PyMuPDF(fitz)` 作为扫描/图片型 PDF 的 fallback 提取器。

### 向量库运维（切换 embedding 模型时）

默认使用 DashScope Qwen 嵌入模型。若切换到 OpenAI / 本地 BGE 等不同维度模型，需重置向量库，否则检索维度不匹配：
```bash
cd backend
python -m scripts.reset_chroma list                       # 查看全部集合
python -m scripts.reset_chroma reset                      # 删除当前集合（自动惰性重建）
python -m scripts.reset_chroma reset --all                # 删除全部集合
```

### 知识库文档入库（加载 → 分片 → 向量化 → 写入 Chroma）

把企业文档放入 `backend/data/documents`（递归扫描 `.txt/.md/.pdf`），执行：
```bash
cd backend
python -m scripts.ingest_kb                    # 入库全部文档
python -m scripts.ingest_kb --dir ./my/docs    # 指定源目录
python -m scripts.ingest_kb --clear            # 先清空向量集合再入库
```
入库后即可被 `search_knowledge_base` 工具语义检索到，供 Agent 回答引用。

> 除 CLI 脚本外，前端「知识库文档」附件通过 `POST /api/v1/knowledge/upload` 实时入库（支持 `.txt/.md/.pdf`，无文字层扫描件返回明确 400 错误），两者复用同一分片/向量化逻辑。

### 智能体编排（LangGraph）
核心图定义在 [graph.py](backend/app/agents/graph.py)：

```
START ──▶ agent(LLM + Tools) ──▶ conditional ──▶ tools(执行)
              ▲                                   │
              └─────────────── END ◀──────────────┘
```
- **agent 节点**：带会话历史调用 LLM，模型可返回工具调用。
- **tools 节点**：自动执行模型申请的工具，结果回流给模型。
- 存在工具调用则继续循环，否则 `END` 结束。

### 记忆方案
- **短期记忆（会话级）**：`RedisSessionMemory` 用 Redis List 存储最近 N 条消息，带 TTL 自动过期。
- **长期记忆（知识库）**：`VectorStore` 封装 ChromaDB，企业文档切片嵌入后按语义检索。

### MCP 集成
- 内置 FastMCP 示例服务器 [database_server.py](backend/mcp_servers/core/database_server.py)，可独立运行。
- 客户端 [client.py](backend/app/mcp/client.py) 读取 `backend/mcp_servers/config.yaml`，动态连接外部 MCP 服务器并暴露工具给 Agent。

---

## API 接口

Base URL：`/api/v1`。前端统一经 `frontend/app/api` 下的 Route Handler / 通用代理转发到后端 `8900`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查（分项探活 MySQL / Redis / Chroma）|
| POST | `/agent/chat` | 非流式对话（body 需含 `session_id`, `message`）|
| POST | `/agent/chat/stream` | SSE 流式对话，逐 token 返回 |
| GET | `/chat?session_id=&message=` | 兼容 EventSource 的流式对话（只支持 GET，query 传参）|
| GET | `/session?sort=...` | 会话列表，`sort` = `recent`/`oldest`/`messages` |
| GET | `/session/{session_id}/messages` | 获取某会话历史 |
| POST | `/session/{session_id}/clear` | 删除会话（清空其 Redis 记录，前端点击删除按钮时调用）|
| POST | `/knowledge/upload` | 知识库文档上传入库（`.txt/.md/.markdown/.pdf`，multipart 字段 `file`）|
| GET | `/tickets?limit=` | 工单列表（按用户查询最新工单，`limit` 1–50）|

### 流式对话
- **EventSource 前端主链路**：浏览器 `EventSource` 以 GET 连 `/api/v1/chat`；前端 [route.ts](frontend/app/api/v1/chat/route.ts) 用 `fetch(cache:"no-store")` 把后端流式 body 实时透传，避免 Next 运行时缓冲，实现逐字打字机效果。
- **POST 流式**：`POST /api/v1/agent/chat/stream` 同样经前端 Route Handler 转发并 `cache:"no-store"`。

`POST /agent/chat` 示例：
```bash
curl -X POST http://localhost:8900/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"s1","message":"你好，请介绍一下你们的产品"}'
```

响应：
```json
{ "session_id": "s1", "reply": "...", "usage": {} }
```

### 知识库上传
前端「知识库文档」附件即调用 `POST /api/v1/knowledge/upload`：
```bash
curl -F "file=@./doc.pdf" http://localhost:8900/api/v1/knowledge/upload
# → {"chunks": 103, "filename": "doc.pdf"}
```
- 支持文本型 PDF（`pypdf`）、扫描/图片型 PDF（`PyMuPDF` fallback）。
- 无文字层的扫描件会返回 **400** 及明确中文错误，而不是静默入 0 片。
- 大文档分片较多时，向量库按批量（每批 20）写入，规避 embedding 网关批量上限。

---

## 数据模型（MySQL）

由 `backend/sql/init.sql` 初始化：

- **agents**：智能体定义（名称、系统提示词、默认模型、状态）。
- **session_records**：会话消息流水（用于审计与续接）。

> ORM 模型位于 [app/db/models](backend/app/db/models)，迁移可基于 `alembic` 扩展。

---

## 测试

```bash
cd backend
pytest -v          # 单元测试（含 config 解析用例）
pytest -m integration   # 集成测试（需 MySQL/Redis 已启动）
```

---

## 常见问题

**Q: ChromaDB 启动报编译错误？**
本机为 **Python 3.13+** 时，`chromadb 0.5.x` 无预编译 wheel，会在 `pip install` 时从源码编译 `chroma-hnswlib`（C++）。解决方案：① 用 **方式 A（Docker，python:3.11）** 运行后端；② 或本机安装 Python 3.12 并重建 venv。安装时如遇 `langchain-chroma` 与 `chromadb` 版本互斥，请保持 `chromadb==0.5.23` + `langchain-chroma==0.1.4` 组合。

**Q: 后端启动报 `ValidationError`（SESSION_TTL_SECONDS 等）？**
`.env` 中**变量值与行尾注释必须分两行**写，如 `SESSION_TTL_SECONDS=604800`（注释另起一行以 `#` 开头）。pydantic-settings 会把行尾 `  # 7 天` 一并读入导致整数解析失败。

**Q: 前端请求后端 404 / 连接不上？**
确认后端监听 `8900`，`NEXT_PUBLIC_BACKEND_URL` 默认 `http://localhost:8900`。前端 API 经 `frontend/app/api` 转发：普通 JSON 请求走通用代理 `app/api/[...path]/route.ts`，流式端点由更具体的 Route Handler（`app/api/v1/chat`、`app/api/v1/agent/chat/stream`）优先接管。不再依赖 `next.config.js` 的 `rewrites`（其会对 SSE 流式缓冲）。

**Q: 如何切换/接入其他 LLM？**
修改 `.env` 中的 `DEEPSEEK_API_KEY` / `OPENAI_BASE_URL` / `LLM_CHAT_MODEL` 三项即可，无需改代码。向量 embedding 依赖 `EMBEDDING_PROVIDER` 独立配置。

---

## 路线图（建议扩展）

已实现：
- [x] 前端流式响应（SSE / EventSource 逐字打字机，`cache: no-store` 透传）
- [x] 会话列表按时间/活跃度排序（`recent` / `oldest` / `messages`）
- [x] 会话删除（后端清 Redis，刷新持久）
- [x] 知识库前端上传（`.txt/.md/.pdf`，扫描件友好报错）
- [x] 工单面板（右侧抽屉 `GET /api/v1/tickets`）

待扩展：
- [ ] Alembic 数据库迁移管理
- [ ] JWT 鉴权接入业务用户体系
- [ ] 可视化 Agent 编排 / 观测（LangSmith / 自研 trace）
- [ ] 多智能体协作（Manager/Worker 模式）
- [ ] ChromaDB 独立容器化部署
- [ ] CI/CD（GitHub Actions 构建镜像）

---

## License
内部项目，保留所有权利。