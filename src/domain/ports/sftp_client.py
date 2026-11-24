from abc import ABC, abstractmethod
from typing import BinaryIO

from src.domain.entities.sftp_credentials import SftpCredentials


class SftpClient(ABC):
    """Port for writing files to an SFTP destination."""

    @abstractmethod
    def connect(self, credentials: SftpCredentials) -> None:
        """Open an SFTP connection."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close the SFTP connection."""
        raise NotImplementedError

    @abstractmethod
    def upload(
        self,
        file_stream: BinaryIO,
        remote_path: str,
        filename: str,
    ) -> str:
        """Upload a stream into the configured remote directory."""
        raise NotImplementedError
