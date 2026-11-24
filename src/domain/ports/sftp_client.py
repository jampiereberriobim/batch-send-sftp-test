from abc import ABC, abstractmethod
from typing import BinaryIO

from src.domain.entities.remote_file import RemoteFile
from src.domain.entities.sftp_credentials import SftpCredentials


class SftpClient(ABC):
    """
    Contract for SFTP operations.
    """

    @abstractmethod
    def connect(
        self,
        credentials: SftpCredentials
    ) -> None:
        """
        Opens an SFTP connection.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Closes the SFTP connection.
        """
        pass

    @abstractmethod
    def list_files(
        self,
        remote_path: str,
        pattern: str,
        recursive: bool
    ) -> list[RemoteFile]:
        """
        Lists remote files.
        """
        pass

    @abstractmethod
    def download(
        self,
        remote_file: RemoteFile
    ) -> BinaryIO:
        """
        Downloads a remote file.
        """
        pass