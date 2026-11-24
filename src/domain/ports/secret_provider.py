from abc import ABC, abstractmethod

from src.domain.entities.sftp_credentials import SftpCredentials


class SecretProvider(ABC):
    """
    Contract for retrieving SFTP credentials.
    """

    @abstractmethod
    def get_secret(
        self,
        secret_name: str
    ) -> SftpCredentials:
        """
        Retrieves SFTP credentials.

        Args:
            secret_name: AWS Secrets Manager secret name.

        Returns:
            SftpCredentials
        """
        pass