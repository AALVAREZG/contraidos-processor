"""File handling service"""

import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from ..config import settings


class FileService:
    """Service for file operations"""

    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.export_dir = settings.export_dir

    async def save_upload(self, file: UploadFile) -> tuple[str, Path]:
        """
        Save uploaded file.

        Returns:
            Tuple of (upload_id, file_path)
        """
        # Generate unique ID
        upload_id = str(uuid.uuid4())

        # Create unique filename
        file_extension = Path(file.filename).suffix
        filename = f"{upload_id}{file_extension}"
        file_path = self.upload_dir / filename

        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return upload_id, file_path

    def get_file_path(self, upload_id: str, extension: str = "") -> Optional[Path]:
        """Get file path for upload_id"""
        if extension:
            file_path = self.upload_dir / f"{upload_id}{extension}"
        else:
            # Try to find file with any extension
            for ext in settings.allowed_extensions:
                file_path = self.upload_dir / f"{upload_id}{ext}"
                if file_path.exists():
                    return file_path
            return None

        return file_path if file_path.exists() else None

    def delete_file(self, file_path: Path) -> bool:
        """Delete a file"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception:
            pass
        return False

    def get_export_path(self, export_id: str, extension: str) -> Path:
        """Get export file path"""
        return self.export_dir / f"{export_id}{extension}"
