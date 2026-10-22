"""知识库文档入库：加载 → 分片 → 向量化 → 写入 Chroma。

支持的源文件（递归扫描 KB_DOCS_DIR）：
    .txt / .md / .markdown   纯文本读取
    .pdf                     需 pypdf（未安装时会跳过并提示）

用法（在 backend 目录）：
    python -m scripts.ingest_kb                    # 入库默认目录全部文档
    python -m scripts.ingest_kb --dir ./my/docs    # 指定源目录
    python -m scripts.ingest_kb --clear            # 先清空向量集合再入库
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 确保可导入 backend.app

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.memory.chroma_store import VectorStore

# 纯文本类扩展名
_TEXT_EXTS = {".txt", ".md", ".markdown", ".html", ".json"}


def load_file(path: Path) -> str:
    """读取单个文档为文本；PDF 需额外依赖。"""
    ext = path.suffix.lower()
    if ext == ".pdf":
        # 惰性导入，缺依赖时抛异常由上层跳过
        from langchain_community.document_loaders import PyPDFLoader

        docs = PyPDFLoader(str(path)).load()
        return "\n\n".join(d.page_content for d in docs)
    return path.read_text(encoding="utf-8", errors="ignore")


async def ingest(sources_dir: Path, clear: bool) -> None:
    store = VectorStore()

    if clear:
        store.reset_collection()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.KB_CHUNK_SIZE,
        chunk_overlap=settings.KB_CHUNK_OVERLAP,
    )

    total_chunks = 0
    files = list(sources_dir.rglob("*"))
    docs = [f for f in files if f.is_file() and f.suffix.lower() in _TEXT_EXTS.union({".pdf"})]

    if not docs:
        print(f"[warn] 目录 {sources_dir} 下未发现可入库文档。")
        return

    for path in docs:
        try:
            text = load_file(path)
            if not text.strip():
                continue
            chunks = splitter.split_text(text)
            ids = [f"{path.stem}-{i}" for i in range(len(chunks))]
            metadatas = [{"source": str(path), "chunk_index": i} for i in range(len(chunks))]

            store.add_texts(chunks, metadatas, ids)
            total_chunks += len(chunks)
            print(f"[+]{path.relative_to(sources_dir)} -> {len(chunks)} chunks")
        except Exception as exc:
            print(f"[!] 跳过 {path.name}: {exc}")

    print(f"\n[done] 共入库 {total_chunks} 个分片到集合: {settings.CHROMA_COLLECTION}")


def main() -> int:
    parser = argparse.ArgumentParser(description="知识库文档入库")
    parser.add_argument("--dir", default=settings.KB_DOCS_DIR, help="源文档目录（默认读配置）")
    parser.add_argument("--clear", action="store_true", help="入库前先清空向量集合")
    args = parser.parse_args()

    sources_dir = Path(args.dir)
    if not sources_dir.exists():
        print(f"[error] 目录不存在: {sources_dir}")
        return 1

    asyncio.run(ingest(sources_dir, clear=args.clear))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())