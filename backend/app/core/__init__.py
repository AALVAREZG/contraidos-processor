"""Core module initialization and plugin registration"""

from .parsers import get_parser_factory
from .parsers.contraidos_parser import ContraidosExcelParser
from .analyzers import get_analyzer_factory
from .analyzers.contraidos_analyzer import ContraidosAnalyzer


def register_contraidos_plugins():
    """Register contraídos parser and analyzer"""
    # Register parser
    parser_factory = get_parser_factory()
    parser_factory.register_parser(ContraidosExcelParser())

    # Register analyzer
    analyzer_factory = get_analyzer_factory()
    analyzer_factory.register_analyzer("contraidos", ContraidosAnalyzer)


# Auto-register on import
register_contraidos_plugins()

__all__ = ["get_parser_factory", "get_analyzer_factory", "register_contraidos_plugins"]
