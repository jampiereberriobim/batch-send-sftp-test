from datetime import datetime
from io import BytesIO

import pyarrow as pa
import pyarrow.parquet as pq
from botocore.client import BaseClient

from src.domain.ports.metadata_repository import MetadataRepository
from src.infrastructure.aws.s3_client import S3Client


class S3MetadataRepository(MetadataRepository):
    """AWS S3 implementation of MetadataRepository."""

    def __init__(
        self,
        s3_client: S3Client,
        bucket_name: str,
    ) -> None:
        self._client: BaseClient = s3_client.client
        self._bucket_name = bucket_name

    def save(self, metadata: dict) -> None:
        # Use the execution end time consistently for partitions and filename.
        execution_time = datetime.fromisoformat(metadata["end_time"])
        report_name = metadata["report_name"]
        execution_id = str(metadata["execution_id"]).replace("-", "")[:8]
        timestamp = execution_time.strftime("%Y%m%d%H%M%S")

        key = (
            f"SFTP/{report_name}/"
            f"year={execution_time.year}/"
            f"month={execution_time.month}/"
            f"day={execution_time.day}/"
            f"{report_name}_{execution_id}_{timestamp}.parquet"
        )

        table = pa.Table.from_pylist([metadata])
        buffer = BytesIO()
        pq.write_table(table, buffer, compression="snappy")
        buffer.seek(0)

        self._client.upload_fileobj(
            Fileobj=buffer,
            Bucket=self._bucket_name,
            Key=key,
        )
