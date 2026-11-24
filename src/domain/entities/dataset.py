from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Dataset:
    """
    Represents the configuration of a dataset to be ingested from an SFTP server.

    Each dataset corresponds to a logical folder or file source inside an
    integration and contains all the information required to execute the
    ingestion process.
    """

    integration: str
    name: str

    remote_path: str
    file_pattern: str

    destination_bucket: str
    destination_prefix: str

    enabled: bool

    recursive: bool = False

    archive_path: Optional[str] = None

    delete_after_download: bool = False