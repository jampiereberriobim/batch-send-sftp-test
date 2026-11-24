import json

from botocore.client import BaseClient

from src.domain.entities.sftp_credentials import SftpCredentials
from src.domain.ports.secret_provider import SecretProvider

from src.infrastructure.aws.secrets_manager_client import (
    SecretsManagerClient,
)


class SecretsManagerProvider(SecretProvider):
    """
    AWS Secrets Manager implementation of SecretProvider.
    """

    def __init__(
        self,
        secrets_manager_client: SecretsManagerClient,
    ) -> None:

        self._client: BaseClient = (
            secrets_manager_client.client
        )

    def get_secret(
        self,
        secret_name: str,
    ) -> SftpCredentials:

        response = self._client.get_secret_value(
            SecretId=secret_name
        )

        secret = json.loads(response["SecretString"])

        credentials = json.loads(secret["sftp_qa_2"])
        
        return SftpCredentials(
            host=credentials["host"],
            port=int(credentials["port"]),
            username=credentials["username"],
            password=credentials.get("password"),
            private_key=credentials.get("private_key"),
            private_key_passphrase=credentials.get("private_key_passphrase"),
        )