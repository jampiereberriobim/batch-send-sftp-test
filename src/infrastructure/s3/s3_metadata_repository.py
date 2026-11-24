from io import BytesIO

import pyarrow as pa
import pyarrow.parquet as pq
from botocore.client import BaseClient

from src.domain.ports.metadata_repository import MetadataRepository
from src.infrastructure.aws.s3_client import S3Client
from datetime import datetime

class S3MetadataRepository(MetadataRepository):
    """
    AWS S3 implementation of MetadataRepository.
    """

    def __init__(
        self,
        s3_client: S3Client,
        bucket_name: str,
        metadata_prefix: str,
    ) -> None:

        self._client: BaseClient = s3_client.client
        self._bucket_name = bucket_name
        self._metadata_prefix = metadata_prefix.rstrip("/")

    def save(
        self,
        metadata: dict,
    ) -> None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        key = (
            f"{self._metadata_prefix}/"
            f"integration={metadata['integration']}/"
            f"dataset={metadata['dataset']}/"
            f"year={datetime.utcnow():%Y}/"
            f"month={datetime.utcnow():%m}/"
            f"day={datetime.utcnow():%d}/"
            f"{timestamp}.parquet"
        )

        table = pa.Table.from_pylist([metadata])

        buffer = BytesIO()

        pq.write_table(
            table,
            buffer,
            compression="snappy",
        )

        buffer.seek(0)

        self._client.upload_fileobj(
            Fileobj=buffer,
            Bucket=self._bucket_name,
            Key=key,
        )