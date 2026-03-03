from abc import ABC, abstractmethod
from dataclasses import dataclass
import dataclasses
from typing import Any
import logging
import time


@dataclass
class ToolResult:
    success: bool
    output: Any
    error: str | None = None
    duration_ms: float = 0.0
    
    def __post_init__(self):
        if not self.success and self.error is None:
            raise ValueError("ToolResult with success=False must include an error message")


class BaseTool(ABC):
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{self.name}")

    @abstractmethod
    def validate_input(self, **kwargs: Any) -> None:
        """Validate input arguments before execution. Raise ValueError on invalid input."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with validated arguments and return a ToolResult."""

    def run(self, **kwargs: Any) -> ToolResult:
        """Validate inputs, execute the tool, time it, and return a ToolResult.

        Never raises — all errors are captured in ToolResult(success=False).
        """
        start = time.monotonic()
        try:
            self.validate_input(**kwargs)
            result = self.execute(**kwargs)
            return dataclasses.replace(result, duration_ms=(time.monotonic() - start) * 1000)
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            self.logger.error(f"Tool '{self.name}' failed: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration_ms,
            )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r})"
        )