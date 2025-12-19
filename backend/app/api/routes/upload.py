"""File upload routes"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from ...config import settings
from ...services.file_service import FileService
from ...db.schemas import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])
file_service = FileService()


@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for analysis.

    Supports: .xlsx, .xls files

    Returns upload_id to use for analysis.
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}",
        )

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_upload_size / 1024 / 1024:.1f}MB",
        )

    # Save file
    try:
        upload_id, file_path = await file_service.save_upload(file)

        return UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            size_bytes=file_size,
            file_type=file_extension,
            status="uploaded",
            message="File uploaded successfully. Use upload_id to start analysis.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
