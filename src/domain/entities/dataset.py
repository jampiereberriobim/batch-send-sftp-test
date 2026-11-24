from dataclasses import dataclass


@dataclass(frozen=True)
class Dataset:
    """Configuration for transferring files from S3 to an SFTP destination."""

    integration: str
    name: str
    source_bucket: str
    source_prefix: str
    remote_path: str
    enabled: bool
    source_date_template: str = ""
    source_suffix: str = ""
    destination_date_template: str = ""
    recursive: bool = False
