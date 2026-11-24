from dataclasses import dataclass


@dataclass(frozen=True)
class Dataset:
    """Configuration for transferring files from S3 to an SFTP destination."""

    integration: str
    name: str
    source_bucket: str
    source_prefix: str
    date_template: str
    remote_path: str
    enabled: bool
    recursive: bool = False
