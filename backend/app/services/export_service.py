"""Export service for generating reports"""

import uuid
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd


class ExportService:
    """Service for exporting analysis results"""

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir
        self.export_dir.mkdir(exist_ok=True, parents=True)

    def export_to_json(self, analysis_data: Dict[str, Any]) -> tuple[str, Path]:
        """
        Export analysis to JSON.

        Returns:
            Tuple of (export_id, file_path)
        """
        export_id = str(uuid.uuid4())
        file_path = self.export_dir / f"{export_id}.json"

        # Convert datetime objects to strings
        def json_serializer(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=json_serializer)

        return export_id, file_path

    def export_to_excel(
        self, analysis_data: Dict[str, Any], original_df: pd.DataFrame = None
    ) -> tuple[str, Path]:
        """
        Export analysis to Excel with multiple sheets.

        Returns:
            Tuple of (export_id, file_path)
        """
        export_id = str(uuid.uuid4())
        file_path = self.export_dir / f"{export_id}.xlsx"

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Sheet 1: Summary
            summary_data = []
            for key, value in analysis_data.get("summary", {}).items():
                summary_data.append({"Métrica": key, "Valor": str(value)})
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Resumen", index=False)

            # Sheet 2: Calculations (if available)
            if "details" in analysis_data and "calculations" in analysis_data["details"]:
                calc_data = []
                for key, value in analysis_data["details"]["calculations"].items():
                    calc_data.append({"Concepto": key, "Valor": value})
                pd.DataFrame(calc_data).to_excel(writer, sheet_name="Cálculos", index=False)

            # Sheet 3: Validation Issues
            if "validation" in analysis_data:
                issues = analysis_data["validation"].get("issues", [])
                if issues:
                    pd.DataFrame(issues).to_excel(writer, sheet_name="Problemas", index=False)

                warnings = analysis_data["validation"].get("warnings", [])
                if warnings:
                    pd.DataFrame(warnings).to_excel(writer, sheet_name="Advertencias", index=False)

            # Sheet 4: Original data (if provided)
            if original_df is not None:
                original_df.to_excel(writer, sheet_name="Datos Originales", index=False)

        return export_id, file_path
