from botocore.client import BaseClient

from src.infrastructure.aws.boto_session import BotoSession


class S3Client:
    def __init__(self):
        self._client: BaseClient = BotoSession.session().client("s3")

    @property
    def client(self) -> BaseClient:
        return self._client
