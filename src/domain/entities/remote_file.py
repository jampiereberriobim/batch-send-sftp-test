from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RemoteFile:
    """
    Represents a file available on a remote SFTP server.
    """

    name: str

    path: str

    size: int

    modified_at: datetime