from abc import ABC, abstractmethod
from typing import BinaryIO

from src.domain.entities.remote_file import RemoteFile


class StorageClient(ABC):
    """
    Contract for storing files.
    """

    @abstractmethod
    def upload(
        self,
        file_stream: BinaryIO,
        remote_file: RemoteFile,
        destination_prefix: str
    ) -> str:
        """
        Uploads a file.

        Returns:
            Object key.
        """
        pass