from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseIngestor(ABC):
    """Base contract for ingestion pipelines."""

    @abstractmethod
    async def ingest(self, data: dict[str, Any]) -> dict[str, Any]:
        """Ingest data and return a structured result payload."""
        raise NotImplementedError
