import os
from dataclasses import asdict
from datetime import date

from src.application.dto.execution_request import ExecutionRequest
from src.application.use_cases.execute_dataset_use_case import ExecuteDatasetUseCase
from src.infrastructure.aws.dynamodb_client import DynamoDbClient
from src.infrastructure.aws.s3_client import S3Client
from src.infrastructure.aws.secrets_manager_client import SecretsManagerClient
from src.infrastructure.dynamodb.dataset_repository_impl import DatasetRepositoryImpl
from src.infrastructure.dynamodb.integration_repository_impl import IntegrationRepositoryImpl
from src.infrastructure.s3.s3_metadata_repository import S3MetadataRepository
from src.infrastructure.s3.s3_notification_repository import S3NotificationRepository
from src.infrastructure.s3.s3_storage_client import S3StorageClient
from src.infrastructure.secrets.secrets_manager_provider import SecretsManagerProvider
from src.infrastructure.sftp.paramiko_sftp_client import ParamikoSftpClient


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def lambda_handler(event, context):
    dynamodb = DynamoDbClient()
    s3 = S3Client()
    secrets = SecretsManagerClient()

    dataset_repository = DatasetRepositoryImpl(
        dynamodb_client=dynamodb,
        table_name=os.environ["DATASET_TABLE"],
    )
    integration_repository = IntegrationRepositoryImpl(
        dynamodb_client=dynamodb,
        table_name=os.environ["INTEGRATION_TABLE"],
    )
    secret_provider = SecretsManagerProvider(secrets_manager_client=secrets)
    sftp_client = ParamikoSftpClient()
    storage_client = S3StorageClient(s3_client=s3)
    metadata_repository = S3MetadataRepository(
        s3_client=s3,
        bucket_name=os.environ["METADATA_BUCKET"],
    )
    notification_repository = S3NotificationRepository(
        s3_client=s3,
        bucket_name=os.environ["NOTIFICATION_BUCKET"],
    )

    use_case = ExecuteDatasetUseCase(
        dataset_repository=dataset_repository,
        integration_repository=integration_repository,
        secret_provider=secret_provider,
        sftp_client=sftp_client,
        storage_client=storage_client,
        metadata_repository=metadata_repository,
        notification_repository=notification_repository,
    )

    request = ExecutionRequest(
        integration=event["integration"],
        dataset=event["dataset"],
        start_date=_parse_date(event.get("start_date")),
        end_date=_parse_date(event.get("end_date")),
    )
    return asdict(use_case.execute(request))
