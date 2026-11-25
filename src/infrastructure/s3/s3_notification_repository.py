import json

from botocore.client import BaseClient

from src.domain.ports.notification_repository import NotificationRepository
from src.infrastructure.aws.s3_client import S3Client


class S3NotificationRepository(NotificationRepository):
    """Stores process notifications as JSON objects in S3."""

    def __init__(self, s3_client: S3Client, bucket_name: str) -> None:
        self._client: BaseClient = s3_client.client
        self._bucket_name = bucket_name

    def save(self, notification: dict) -> None:
        process_name = notification["process_name"].upper()
        key = f"NOTIFICACIONES/{process_name}/{process_name}.json"
        body = json.dumps(
            notification,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

        self._client.put_object(
            Bucket=self._bucket_name,
            Key=key,
            Body=body,
            ContentType="application/json",
        )
