"""Base sourcer class for all data sources."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class SourcedContent:
    """Represents content retrieved from a source."""

    def __init__(
        self,
        title: str,
        content: str,
        url: Optional[str] = None,
        published_date: Optional[datetime] = None,
        author: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.title = title
        self.content = content
        self.url = url
        self.published_date = published_date
        self.author = author
        self.metadata = metadata or {}
        self.retrieved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "author": self.author,
            "metadata": self.metadata,
            "retrieved_at": self.retrieved_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<SourcedContent: {self.title[:50]}...>"


class BaseSourcer(ABC):
    """Abstract base class for all data sourcers."""

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the sourcer.

        Args:
            name: Optional name for this sourcer instance
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    async def fetch(self, **kwargs) -> List[SourcedContent]:
        """
        Fetch content from the source.

        Returns:
            List of SourcedContent objects

        Raises:
            Exception: If fetching fails
        """
        pass

    @abstractmethod
    def validate_config(self, **kwargs) -> bool:
        """
        Validate the configuration for this sourcer.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
