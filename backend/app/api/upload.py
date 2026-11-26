import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user
from app.config import settings
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        return {"detail": "仅支持 jpg/png/webp"}

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    content = await file.read()
    filepath.write_bytes(content)

    return {"url": f"{settings.PUBLIC_BASE_URL}/static/uploads/{filename}"}