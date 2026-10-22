"""配置解析单元测试。"""
from app.core.config import Settings


def test_settings_defaults():
    s = Settings()  # 使用默认值
    assert s.APP_NAME == "enterprise-agent-system"
    assert "mysql+pymysql" in s.SQLALCHEMY_DATABASE_URI
    assert s.REDIS_URL.startswith("redis://")


def test_redis_url_with_password():
    s = Settings(REDIS_PASSWORD="secret", REDIS_HOST="redis", REDIS_PORT=6379, REDIS_DB=2)
    assert s.REDIS_URL == "redis://:secret@redis:6379/2"