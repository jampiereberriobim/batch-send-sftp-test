from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResponse:
    """
    Represents the execution result returned by the application layer.
    """

    integration: str

    dataset: str

    processed_files: int

    uploaded_files: int

    success: bool

    message: str