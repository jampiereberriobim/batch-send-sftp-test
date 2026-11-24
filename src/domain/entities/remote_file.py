from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RemoteFile:
    """A file discovered in the source object storage."""

    name: str
    path: str
    size: int
    modified_at: datetime
