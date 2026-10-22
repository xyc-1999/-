"""初始化数据库表结构：python -m scripts.init_db。"""
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 确保可导入 backend.app

from app.core.config import settings
from app.db.session import Base, engine


def init_db() -> None:
    print(f"Connecting to: {engine.url.render_as_string(hide_password=True)}")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    init_db()