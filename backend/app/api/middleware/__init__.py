"""API 中间件层：鉴权、限流、日志可在此扩展。"""

# 示例：如果把中间件直接放在 routes 层，这里可放置通用依赖，
# 需要的话在 main.py 中注册，如：
# app.add_middleware(LoggingMiddleware)