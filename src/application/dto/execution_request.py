from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ExecutionRequest:
    """Request to transfer one dataset, optionally for a date range."""

    integration: str
    dataset: str
    start_date: date | None = None
    end_date: date | None = None
