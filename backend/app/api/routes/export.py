"""Export routes"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ...services.analysis_service import AnalysisService
from ...services.export_service import ExportService
from ...config import settings
from ...db.schemas import ExportRequest, ExportResponse

router = APIRouter(prefix="/export", tags=["export"])
analysis_service = AnalysisService()
export_service = ExportService(settings.export_dir)


@router.post("/{analysis_id}", response_model=ExportResponse)
async def export_analysis(analysis_id: str, request: ExportRequest):
    """
    Export analysis results to specified format.

    Supported formats:
    - json: JSON file with complete results
    - excel: Excel workbook with multiple sheets
    """
    # Get analysis data
    analysis_data = analysis_service.get_analysis(analysis_id)
    if not analysis_data:
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")

    try:
        if request.format == "json":
            export_id, file_path = export_service.export_to_json(analysis_data)
            filename = f"analysis_{analysis_id}.json"

        elif request.format == "excel":
            export_id, file_path = export_service.export_to_excel(analysis_data)
            filename = f"analysis_{analysis_id}.xlsx"

        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported format: {request.format}"
            )

        return ExportResponse(
            export_id=export_id,
            download_url=f"/api/v1/export/download/{export_id}",
            filename=filename,
            format=request.format,
            size_bytes=file_path.stat().st_size,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.get("/download/{export_id}")
async def download_export(export_id: str):
    """Download exported file"""
    # Try different extensions
    for ext in [".json", ".xlsx", ".pdf"]:
        file_path = export_service.export_dir / f"{export_id}{ext}"
        if file_path.exists():
            return FileResponse(
                path=file_path,
                filename=file_path.name,
                media_type="application/octet-stream",
            )

    raise HTTPException(status_code=404, detail=f"Export not found: {export_id}")
