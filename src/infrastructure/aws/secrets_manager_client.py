from botocore.client import BaseClient

from src.infrastructure.aws.boto_session import BotoSession


class SecretsManagerClient:

    def __init__(self):

        self._client: BaseClient = (
            BotoSession.session().client(
                "secretsmanager"
            )
        )

    @property
    def client(self) -> BaseClient:
        return self._client