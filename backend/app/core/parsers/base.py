"""Base file parser for extensibility"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import pandas as pd


@dataclass
class ParserResult:
    """Result from parsing a file"""

    success: bool
    dataframe: Optional[pd.DataFrame] = None
    file_type: Optional[str] = None
    metadata: dict = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseFileParser(ABC):
    """
    Base class for all file parsers.

    This abstract class defines the interface that all parsers must implement.
    New file formats (PDF, CSV, etc.) can be added by creating new parsers
    that inherit from this class.

    Example:
        class PDFParser(BaseFileParser):
            def can_handle(self, file_path: Path) -> bool:
                return file_path.suffix.lower() == '.pdf'

            def parse(self, file_path: Path) -> ParserResult:
                # PDF parsing logic
                pass
    """

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if this parser can handle the file
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> ParserResult:
        """
        Parse the file and return standardized DataFrame.

        Args:
            file_path: Path to the file to parse

        Returns:
            ParserResult with DataFrame and metadata
        """
        pass

    @abstractmethod
    def validate_structure(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """
        Validate that the DataFrame has the expected structure.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass

    def get_file_info(self, file_path: Path) -> dict:
        """
        Get basic file information.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file metadata
        """
        return {
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            "extension": file_path.suffix.lower(),
            "parser": self.__class__.__name__
        }
