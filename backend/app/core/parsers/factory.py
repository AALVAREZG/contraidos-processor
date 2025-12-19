"""Parser factory for automatic parser selection"""

from pathlib import Path
from typing import List, Type, Optional
from .base import BaseFileParser


class FileParserFactory:
    """
    Factory for automatically selecting the appropriate parser.

    This factory pattern allows easy addition of new parsers without
    modifying existing code. Simply create a new parser class and
    register it with the factory.

    Example:
        # Automatic discovery
        factory = FileParserFactory()
        parser = factory.get_parser(Path("data.xlsx"))

        # Manual registration
        factory.register_parser(MyCustomParser())
    """

    def __init__(self):
        self._parsers: List[BaseFileParser] = []

    def register_parser(self, parser: BaseFileParser) -> None:
        """
        Register a new parser.

        Args:
            parser: Instance of a parser class
        """
        self._parsers.append(parser)

    def get_parser(self, file_path: Path) -> Optional[BaseFileParser]:
        """
        Get the appropriate parser for a file.

        Args:
            file_path: Path to the file

        Returns:
            Parser instance that can handle the file, or None

        Raises:
            ValueError: If no parser can handle the file
        """
        for parser in self._parsers:
            if parser.can_handle(file_path):
                return parser

        raise ValueError(
            f"No parser found for file: {file_path.name}. "
            f"Supported parsers: {[p.__class__.__name__ for p in self._parsers]}"
        )

    def get_supported_extensions(self) -> set[str]:
        """Get all supported file extensions."""
        extensions = set()
        for parser in self._parsers:
            if hasattr(parser, "supported_extensions"):
                extensions.update(parser.supported_extensions)
        return extensions


# Global factory instance
_factory_instance: Optional[FileParserFactory] = None


def get_parser_factory() -> FileParserFactory:
    """Get the global parser factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = FileParserFactory()
        # Auto-register parsers will happen when they're imported
    return _factory_instance
