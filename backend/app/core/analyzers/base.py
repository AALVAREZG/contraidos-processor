"""Base analyzer for extensibility"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class AnalysisResult:
    """Result from analyzing data"""

    success: bool
    analysis_type: str
    summary: dict = field(default_factory=dict)
    details: dict = field(default_factory=dict)
    validation: dict = field(default_factory=dict)
    chart_data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    error: Optional[str] = None


class BaseAnalyzer(ABC):
    """
    Base class for all data analyzers.

    This abstract class defines the interface for all analyzers.
    New analysis types (balance sheets, invoices, etc.) can be added
    by creating new analyzer classes that inherit from this class.

    Example:
        class BalanceSheetAnalyzer(BaseAnalyzer):
            def get_analysis_type(self) -> str:
                return "balance_sheet"

            def analyze(self) -> AnalysisResult:
                # Analysis logic
                pass
    """

    def __init__(self, df: pd.DataFrame, metadata: dict = None):
        """
        Initialize analyzer.

        Args:
            df: DataFrame with parsed data
            metadata: Optional metadata from parsing
        """
        self.df = df
        self.metadata = metadata or {}
        self.analysis_results: Optional[AnalysisResult] = None

    @abstractmethod
    def get_analysis_type(self) -> str:
        """
        Get the type identifier for this analyzer.

        Returns:
            String identifier (e.g., 'contraidos', 'balance_sheet')
        """
        pass

    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """
        Perform the analysis.

        Returns:
            AnalysisResult with all analysis data
        """
        pass

    @abstractmethod
    def validate_business_rules(self) -> dict:
        """
        Validate domain-specific business rules.

        Returns:
            Dictionary with validation results:
            {
                'is_valid': bool,
                'issues': list,
                'warnings': list
            }
        """
        pass

    @abstractmethod
    def get_chart_data(self) -> dict:
        """
        Get data formatted for visualizations.

        Returns:
            Dictionary with chart configurations and data
        """
        pass

    def export_summary(self) -> dict:
        """
        Get a quick summary of the analysis.

        Returns:
            Dictionary with key metrics
        """
        if not self.analysis_results:
            self.analyze()
        return self.analysis_results.summary

    def export_full_results(self) -> dict:
        """
        Get complete analysis results.

        Returns:
            Full analysis as dictionary
        """
        if not self.analysis_results:
            self.analyze()

        return {
            "analysis_type": self.analysis_results.analysis_type,
            "summary": self.analysis_results.summary,
            "details": self.analysis_results.details,
            "validation": self.analysis_results.validation,
            "chart_data": self.analysis_results.chart_data,
            "metadata": self.analysis_results.metadata,
        }

    @staticmethod
    def can_analyze(df: pd.DataFrame, metadata: dict = None) -> bool:
        """
        Check if this analyzer can handle the given data.

        Args:
            df: DataFrame to check
            metadata: Optional metadata

        Returns:
            True if this analyzer can handle the data
        """
        return False  # Override in subclasses
