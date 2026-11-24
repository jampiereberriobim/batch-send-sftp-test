import json

from botocore.client import BaseClient

from src.domain.entities.sftp_credentials import SftpCredentials
from src.domain.ports.secret_provider import SecretProvider
from src.infrastructure.aws.secrets_manager_client import SecretsManagerClient


class SecretsManagerProvider(SecretProvider):
    """AWS Secrets Manager implementation of SecretProvider."""

    def __init__(
        self,
        secrets_manager_client: SecretsManagerClient,
    ) -> None:
        self._client: BaseClient = secrets_manager_client.client

    def get_secret(self, secret_name: str) -> SftpCredentials:
        response = self._client.get_secret_value(SecretId=secret_name)
        secret_payload = json.loads(response["SecretString"])

        # Support the previous nested secret structure while allowing the
        # secret itself to contain the SFTP connection fields directly.
        credentials = secret_payload.get("sftp_qa_2", secret_payload)
        if isinstance(credentials, str):
            credentials = json.loads(credentials)

        required_fields = ("host", "port", "username", "private_key")
        missing_fields = [
            field for field in required_fields
            if not credentials.get(field)
        ]
        if missing_fields:
            raise ValueError(
                "SFTP secret is missing required SSH fields: "
                + ", ".join(missing_fields)
            )

        return SftpCredentials(
            host=credentials["host"],
            port=int(credentials["port"]),
            username=credentials["username"],
            private_key=credentials["private_key"],
            private_key_passphrase=credentials.get(
                "private_key_passphrase"
            ),
        )
