from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass(frozen=True)
class ExecutionRequest:
    """
    Represents an execution request received by the application layer.
    """

    integration: str

    dataset: str

    #mode: str = "NORMAL"

    #filename: Optional[str] = None
    
    start_date: date | None = None
    end_date: date | None = None