from io import BytesIO
from typing import BinaryIO

from botocore.client import BaseClient

from src.domain.entities.remote_file import RemoteFile
from src.domain.ports.storage_client import StorageClient
from src.infrastructure.aws.s3_client import S3Client


class S3StorageClient(StorageClient):
    """AWS S3 adapter used to list and download source files."""

    def __init__(self, s3_client: S3Client) -> None:
        self._client: BaseClient = s3_client.client

    def list_files(
        self,
        bucket_name: str,
        prefix: str,
        recursive: bool = False,
    ) -> list[RemoteFile]:
        paginator = self._client.get_paginator("list_objects_v2")
        files: list[RemoteFile] = []
        normalized_prefix = prefix.lstrip("/")

        for page in paginator.paginate(
            Bucket=bucket_name,
            Prefix=normalized_prefix,
        ):
            for item in page.get("Contents", []):
                key = item["Key"]
                relative_key = key[len(normalized_prefix):]
                if not recursive and "/" in relative_key.rstrip("/"):
                    continue
                if key.endswith("/"):
                    continue

                files.append(
                    RemoteFile(
                        name=key.rsplit("/", 1)[-1],
                        path=key,
                        size=item.get("Size", 0),
                        modified_at=item["LastModified"],
                    )
                )

        return files

    def download(self, remote_file: RemoteFile) -> BinaryIO:
        response = self._client.get_object(
            Bucket=self._bucket_for_file(remote_file),
            Key=remote_file.path,
        )
        stream = BytesIO(response["Body"].read())
        stream.seek(0)
        return stream

    def _bucket_for_file(self, remote_file: RemoteFile) -> str:
        # The bucket is attached by the use case before download.
        bucket_name = getattr(remote_file, "bucket_name", None)
        if not bucket_name:
            raise ValueError("Source bucket is missing from the source file.")
        return bucket_name
