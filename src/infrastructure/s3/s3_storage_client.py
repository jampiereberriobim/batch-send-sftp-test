from typing import BinaryIO
from datetime import datetime

from botocore.client import BaseClient

from src.domain.entities.remote_file import RemoteFile
from src.domain.ports.storage_client import StorageClient

from src.infrastructure.aws.s3_client import S3Client


class S3StorageClient(StorageClient):
    """
    AWS S3 implementation of StorageClient.
    """

    def __init__(
        self,
        s3_client: S3Client,
        bucket_name: str,
    ) -> None:

        self._client: BaseClient = s3_client.client
        self._bucket_name = bucket_name

    def upload(
        self,
        file_stream: BinaryIO,
        remote_file: RemoteFile,
        integration: str,
        destination_prefix: str,
    ) -> str:

        object_key = self._build_object_key(
            integration=integration,
            destination_prefix=destination_prefix,
            filename=remote_file.name,
        )

        self._client.upload_fileobj(
            Fileobj=file_stream,
            Bucket=self._bucket_name,
            Key=object_key,
        )

        return object_key

    @staticmethod
    def _build_object_key(
        integration: str,
        destination_prefix: str,
        filename: str,
    ) -> str:

        now = datetime.utcnow()

        destination_prefix = destination_prefix.strip("/")

        return (
            f"{integration}/"
            f"{destination_prefix}/"
            f"year={now:%Y}/"
            f"month={now:%m}/"
            f"day={now:%d}/"
            f"{filename}"
        )