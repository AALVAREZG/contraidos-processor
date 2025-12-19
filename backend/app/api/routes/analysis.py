"""Analysis routes"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from ...services.analysis_service import AnalysisService
from ...services.file_service import FileService
from ...db.schemas import (
    AnalysisRequest,
    AnalysisSummaryResponse,
    AnalysisFullResponse,
)

router = APIRouter(prefix="/analysis", tags=["analysis"])
analysis_service = AnalysisService()
file_service = FileService()


@router.post("/{upload_id}")
async def analyze_file(upload_id: str, request: AnalysisRequest = None):
    """
    Start analysis on an uploaded file.

    Args:
        upload_id: ID from upload endpoint
        request: Optional analysis configuration

    Returns:
        Complete analysis results
    """
    # Get file path
    file_path = file_service.get_file_path(upload_id)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"File not found: {upload_id}")

    # Determine analysis type
    analysis_type = request.analysis_type if request else None

    # Run analysis
    try:
        analysis_id, results = await analysis_service.analyze_file(file_path, analysis_type)

        return AnalysisFullResponse(
            analysis_id=analysis_id,
            analysis_type=results["analysis_type"],
            status=results["status"],
            summary=results["summary"],
            details=results["details"],
            validation=results["validation"],
            chart_data=results["chart_data"],
            metadata=results["metadata"],
            created_at=results["created_at"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get complete analysis results by ID"""
    results = analysis_service.get_analysis(analysis_id)

    if not results:
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")

    return AnalysisFullResponse(
        analysis_id=results["analysis_id"],
        analysis_type=results["analysis_type"],
        status=results["status"],
        summary=results["summary"],
        details=results["details"],
        validation=results["validation"],
        chart_data=results["chart_data"],
        metadata=results["metadata"],
        created_at=results["created_at"],
    )


@router.get("/{analysis_id}/summary")
async def get_analysis_summary(analysis_id: str):
    """Get quick summary of analysis"""
    summary = analysis_service.get_analysis_summary(analysis_id)

    if not summary:
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")

    return AnalysisSummaryResponse(**summary)


@router.get("")
async def list_analyses():
    """List all analyses"""
    return analysis_service.list_analyses()
