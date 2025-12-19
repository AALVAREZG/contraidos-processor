"""Analysis service"""

import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from ..core import get_parser_factory, get_analyzer_factory


class AnalysisService:
    """Service for managing analysis operations"""

    def __init__(self):
        self.parser_factory = get_parser_factory()
        self.analyzer_factory = get_analyzer_factory()
        self._analysis_cache: Dict[str, Dict] = {}  # In-memory storage for MVP

    async def analyze_file(
        self, file_path: Path, analysis_type: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Analyze a file.

        Args:
            file_path: Path to file to analyze
            analysis_type: Type of analysis, or None for auto-detect

        Returns:
            Tuple of (analysis_id, results_dict)
        """
        # Step 1: Parse file
        parser = self.parser_factory.get_parser(file_path)
        parse_result = parser.parse(file_path)

        if not parse_result.success:
            raise ValueError(f"Failed to parse file: {parse_result.error}")

        # Step 2: Get analyzer
        if analysis_type:
            analyzer = self.analyzer_factory.create_analyzer(
                analysis_type, parse_result.dataframe, parse_result.metadata
            )
        else:
            # Auto-detect
            analyzer = self.analyzer_factory.auto_detect_analyzer(
                parse_result.dataframe, parse_result.metadata
            )
            if not analyzer:
                raise ValueError("Could not auto-detect analysis type")

        # Step 3: Run analysis
        analysis_result = analyzer.analyze()

        if not analysis_result.success:
            raise ValueError(f"Analysis failed: {analysis_result.error}")

        # Step 4: Store results
        analysis_id = str(uuid.uuid4())
        self._analysis_cache[analysis_id] = {
            "analysis_id": analysis_id,
            "analysis_type": analysis_result.analysis_type,
            "status": "completed",
            "summary": analysis_result.summary,
            "details": analysis_result.details,
            "validation": analysis_result.validation,
            "chart_data": analysis_result.chart_data,
            "metadata": analysis_result.metadata,
            "created_at": datetime.now(),
        }

        return analysis_id, self._analysis_cache[analysis_id]

    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis results by ID"""
        return self._analysis_cache.get(analysis_id)

    def get_analysis_summary(self, analysis_id: str) -> Optional[Dict]:
        """Get quick summary of analysis"""
        analysis = self._analysis_cache.get(analysis_id)
        if not analysis:
            return None

        return {
            "analysis_id": analysis["analysis_id"],
            "analysis_type": analysis["analysis_type"],
            "status": analysis["status"],
            "summary": analysis["summary"],
            "created_at": analysis["created_at"],
        }

    def list_analyses(self) -> list[Dict]:
        """List all analyses"""
        return [
            {
                "analysis_id": aid,
                "analysis_type": data["analysis_type"],
                "status": data["status"],
                "created_at": data["created_at"],
            }
            for aid, data in self._analysis_cache.items()
        ]
