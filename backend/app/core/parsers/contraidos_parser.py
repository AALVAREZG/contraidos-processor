"""Excel parser for contraídos files"""

from pathlib import Path
import pandas as pd
from .base import BaseFileParser, ParserResult


class ContraidosExcelParser(BaseFileParser):
    """
    Parser for contraídos Excel files.

    Expected columns:
    - Nº Operación, Año, Aplicación, Nº Contraido, Importe,
      CPGC, FASE, Fecha, Tercero, Descripción, Estado
    """

    supported_extensions = {".xlsx", ".xls"}

    REQUIRED_COLUMNS = [
        "Nº Operación",
        "Año",
        "Aplicación",
        "Nº Contraido",
        "Importe",
        "CPGC",
        "FASE",
        "Fecha",
        "Tercero",
        "Descripción",
        "Estado",
    ]

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is an Excel file"""
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParserResult:
        """Parse Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)

            # Clean column names
            df.columns = df.columns.str.strip()

            # Validate structure
            is_valid, errors = self.validate_structure(df)

            if not is_valid:
                return ParserResult(
                    success=False,
                    error=f"Invalid file structure: {', '.join(errors)}",
                    file_type="contraidos_excel",
                )

            # Get file metadata
            metadata = self.get_file_info(file_path)
            metadata.update(
                {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                }
            )

            return ParserResult(
                success=True,
                dataframe=df,
                file_type="contraidos_excel",
                metadata=metadata,
            )

        except Exception as e:
            return ParserResult(
                success=False, error=f"Error parsing file: {str(e)}", file_type="contraidos_excel"
            )

    def validate_structure(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """Validate that DataFrame has required columns"""
        errors = []

        # Check for missing columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]

        if missing_columns:
            errors.append(f"Missing columns: {', '.join(missing_columns)}")

        # Check if DataFrame is empty
        if df.empty:
            errors.append("File is empty")

        # Check for required data types
        if not errors and "Importe" in df.columns:
            if not pd.api.types.is_numeric_dtype(df["Importe"]):
                errors.append("Column 'Importe' must contain numeric values")

        return len(errors) == 0, errors
