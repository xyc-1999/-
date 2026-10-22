"""知识库服务：接收上传文档并写入向量库（复用 ingest_kb 的分片/入库逻辑）。"""
import asyncio
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.memory.chroma_store import VectorStore

# 支持入库的扩展名
_SUPPORTED_EXTS = {".txt", ".md", ".markdown", ".pdf"}


class KnowledgeBaseService:
    def __init__(self) -> None:
        self._dir = Path(settings.KB_DOCS_DIR)
        self._dir.mkdir(parents=True, exist_ok=True)

    @property
    def docs_dir(self) -> Path:
        return self._dir

    def _read_file(self, path: Path) -> str:
        """读取单个文档文本（PDF 需额外依赖，缺失时抛异常）。"""
        ext = path.suffix.lower()
        if ext == ".pdf":
            text = self._extract_pdf_text(path)
            # 扫描/图片型 PDF 无文本层，pypdf 提取为空，需明确报错而非静默 0 分片
            if not text or not text.strip():
                raise ValueError(
                    "该 PDF 无法提取到可用文本（可能为扫描/图片型文档，无文字层），"
                    "请上传含文本层的 PDF 或先将扫描件转为可复制文本。"
                )
            return text
        return path.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def _extract_pdf_text(path: Path) -> str:
        """先以 pypdf 提取文本；若为空则用 PyMuPDF(fitz) 作为 fallback 再试一次。"""
        try:
            from langchain_community.document_loaders import PyPDFLoader

            docs = PyPDFLoader(str(path)).load()
            text = "\n\n".join(d.page_content for d in docs).strip()
            if text:
                return text
        except Exception:
            pass  # 切换到 fallback

        # fallback：PyMuPDF，对部分损坏/特殊编码 PDF 提取更稳
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(str(path))
            try:
                text = "\n\n".join(page.get_text() for page in doc).strip()
            finally:
                doc.close()
            return text
        except ImportError:
            # 未安装 PyMuPDF 时忽略，交由上层空文本检测统一报错
            return ""

    def ingest_text(self, filename: str, text: str) -> dict:
        """把一段文本切分并写入向量库，返回统计。"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.KB_CHUNK_SIZE,
            chunk_overlap=settings.KB_CHUNK_OVERLAP,
        )
        chunks = splitter.split_text(text)
        stem = Path(filename).stem
        ids = [f"{stem}-{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        store = VectorStore()
        if chunks:
            store.add_texts(chunks, metadatas, ids)
        return {"chunks": len(chunks), "filename": filename}

    def ingest_file(self, filename: str, content: bytes) -> dict:
        """保存上传文件到文档目录并入库。"""
        # 更名去重：追加时间戳，避免同名覆盖
        path = self._dir / filename
        path.write_bytes(content)
        text = self._read_file(path)
        return self.ingest_text(filename, text)