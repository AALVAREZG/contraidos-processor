"""Pydantic schemas for API requests/responses"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class UploadResponse(BaseModel):
    """Response after file upload"""

    upload_id: str
    filename: str
    size_bytes: int
    file_type: str
    status: str = "uploaded"
    message: str = "File uploaded successfully"


class AnalysisRequest(BaseModel):
    """Request to start analysis"""

    analysis_type: Optional[str] = Field(
        None, description="Type of analysis, or auto-detect if not provided"
    )


class AnalysisSummaryResponse(BaseModel):
    """Quick summary response"""

    analysis_id: str
    analysis_type: str
    status: str
    summary: Dict[str, Any]
    created_at: datetime


class AnalysisFullResponse(BaseModel):
    """Complete analysis response"""

    analysis_id: str
    analysis_type: str
    status: str
    summary: Dict[str, Any]
    details: Dict[str, Any]
    validation: Dict[str, Any]
    chart_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime


class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    detail: Optional[str] = None
    status_code: int = 400


class ExportRequest(BaseModel):
    """Request to export analysis"""

    format: str = Field(..., description="Export format: excel, json, pdf")
    options: Optional[Dict[str, Any]] = None


class ExportResponse(BaseModel):
    """Export response"""

    export_id: str
    download_url: str
    filename: str
    format: str
    size_bytes: int
