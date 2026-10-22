# Python 后端镜像
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /code

# 系统依赖（ChromaDB 需要部分编译工具，按需保留）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖，利用 Docker 层缓存（核心运行时依赖，不含 torch 等可选包）
COPY requirements-core.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-core.txt

# 复制应用代码
COPY . .

EXPOSE 8900

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8900"]