"""知识库路由：文档上传入库。"""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.kb_service import KnowledgeBaseService

router = APIRouter()
kb_service = KnowledgeBaseService()

_SUPPORTED = KnowledgeBaseService().docs_dir  # 触发目录创建


@router.post("/upload", description="上传知识库文档并写入向量库")
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")

    ext = "." + (file.filename.split(".")[-1] or "").lower()
    if ext not in {".txt", ".md", ".markdown", ".pdf"}:
        raise HTTPException(status_code=400, detail="仅支持 .txt / .md / .markdown / .pdf")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    try:
        result = kb_service.ingest_file(file.filename, content)
    except ValueError as exc:
        # 文件内容层面的问题（如扫描件无文本层）属于客户端可修正错误，用 400 返回
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"入库失败：{exc}")

    return {"message": f"已入库 {result['chunks']} 个分片", **result}