import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from app.core.config import get_settings
from app.core.limiter import limiter
from app.services.analyze_image import analyze_image
from app.services.analyze_document import analyze_document

router = APIRouter(prefix="/analyze", tags=["analyze"])
settings = get_settings()

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def _save_upload(upload: UploadFile) -> str:
    ext = Path(upload.filename).suffix.lower()
    temp_name = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(settings.UPLOAD_DIR, temp_name)
    with open(dest, "wb") as f:
        f.write(upload.file.read())
    return dest


@router.post("/image")
@limiter.limit("5/day")
async def analyze_image_endpoint(request: Request, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_IMAGE_EXT:
        raise HTTPException(400, detail=f"صيغة غير مدعومة للصور: {ext}")

    path = _save_upload(file)
    try:
        report = await analyze_image(path)
        return report.to_dict()
    finally:
        if settings.DELETE_FILE_AFTER_ANALYSIS_DEFAULT and os.path.exists(path):
            os.remove(path)


@router.post("/document")
@limiter.limit("5/day")
async def analyze_document_endpoint(request: Request, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_DOC_EXT:
        raise HTTPException(400, detail=f"صيغة غير مدعومة للمستندات: {ext}")
    if ext != ".pdf":
        raise HTTPException(400, detail="حاليًا فقط PDF مدعوم في هذه المرحلة — DOCX/TXT قادمة")

    path = _save_upload(file)
    try:
        report = analyze_document(path)
        return report.to_dict()
    finally:
        if settings.DELETE_FILE_AFTER_ANALYSIS_DEFAULT and os.path.exists(path):
            os.remove(path)
