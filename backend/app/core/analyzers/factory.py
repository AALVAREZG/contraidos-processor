"""Analyzer factory for automatic analyzer selection"""

from typing import List, Type, Optional
import pandas as pd
from .base import BaseAnalyzer


class AnalyzerFactory:
    """
    Factory for automatically selecting the appropriate analyzer.

    This factory allows easy addition of new analyzer types without
    modifying existing code.

    Example:
        factory = AnalyzerFactory()
        analyzer = factory.create_analyzer('contraidos', df)
        results = analyzer.analyze()
    """

    def __init__(self):
        self._analyzer_classes: dict[str, Type[BaseAnalyzer]] = {}

    def register_analyzer(
        self, analysis_type: str, analyzer_class: Type[BaseAnalyzer]
    ) -> None:
        """
        Register a new analyzer type.

        Args:
            analysis_type: String identifier for this analyzer
            analyzer_class: The analyzer class (not instance)
        """
        self._analyzer_classes[analysis_type] = analyzer_class

    def create_analyzer(
        self, analysis_type: str, df: pd.DataFrame, metadata: dict = None
    ) -> BaseAnalyzer:
        """
        Create an analyzer instance.

        Args:
            analysis_type: Type of analysis to perform
            df: DataFrame with data
            metadata: Optional metadata

        Returns:
            Analyzer instance

        Raises:
            ValueError: If analysis type is not registered
        """
        analyzer_class = self._analyzer_classes.get(analysis_type)

        if not analyzer_class:
            raise ValueError(
                f"Unknown analysis type: {analysis_type}. "
                f"Available types: {list(self._analyzer_classes.keys())}"
            )

        return analyzer_class(df, metadata)

    def auto_detect_analyzer(
        self, df: pd.DataFrame, metadata: dict = None
    ) -> Optional[BaseAnalyzer]:
        """
        Automatically detect which analyzer to use.

        Args:
            df: DataFrame to analyze
            metadata: Optional metadata

        Returns:
            Analyzer instance, or None if no suitable analyzer found
        """
        for analyzer_class in self._analyzer_classes.values():
            if analyzer_class.can_analyze(df, metadata):
                return analyzer_class(df, metadata)

        return None

    def get_available_types(self) -> list[str]:
        """Get list of registered analyzer types."""
        return list(self._analyzer_classes.keys())


# Global factory instance
_factory_instance: Optional[AnalyzerFactory] = None


def get_analyzer_factory() -> AnalyzerFactory:
    """Get the global analyzer factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = AnalyzerFactory()
    return _factory_instance
