from abc import ABC, abstractmethod
from typing import BinaryIO

from src.domain.entities.remote_file import RemoteFile


class StorageClient(ABC):
    """Port for reading files from source object storage."""

    @abstractmethod
    def list_files(
        self,
        bucket_name: str,
        prefix: str,
        recursive: bool = False,
    ) -> list[RemoteFile]:
        """List files under a bucket prefix."""
        raise NotImplementedError

    @abstractmethod
    def download(self, remote_file: RemoteFile) -> BinaryIO:
        """Download a source file as a binary stream."""
        raise NotImplementedError
