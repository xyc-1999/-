"""Chroma 向量库运维：查看 / 重建集合。

用于切换 embedding 供应商或模型（如 BGE → Qwen qwen3-text-embedding）后，
清理旧向量避免维度不匹配。删除后下次写入/检索会自动重建同名集合。

用法（在 backend 目录）：
    python -m scripts.reset_chroma list                       # 列出所有集合
    python -m scripts.reset_chroma reset                      # 删除当前配置的集合
    python -m scripts.reset_chroma reset --name my_collection # 删除指定集合
    python -m scripts.reset_chroma reset --all                # 删除全部集合
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 确保可导入 backend.app

from app.core.config import settings
from app.memory.chroma_store import VectorStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Chroma 向量库运维脚本")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("list", help="列出当前向量库中的所有集合")

    p_reset = sub.add_parser("reset", help="删除集合（删除后自动惰性重建）")
    p_reset.add_argument("--name", help="要删除的集合名（默认当前配置值）")
    p_reset.add_argument("--all", action="store_true", help="删除全部集合")

    args = parser.parse_args()

    store = VectorStore()

    if args.action == "list":
        for name in store.list_collections():
            print(name)
        print(f"\n当前配置: provider={settings.EMBEDDING_PROVIDER}, "
              f"model={settings.EMBEDDING_MODEL}, collection={settings.CHROMA_COLLECTION}")
        return 0

    if args.action == "reset":
        if args.all:
            for name in store.list_collections():
                store.reset_collection(name)
            print("[done] 已清空全部集合，下次写入时自动重建。")
        else:
            store.reset_collection(args.name)
            print(f"[done] 集合 {args.name or settings.CHROMA_COLLECTION} 已重置。")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())