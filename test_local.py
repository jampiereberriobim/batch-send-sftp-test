import os
from datetime import date

from src.application.dto.execution_request import ExecutionRequest
from src.application.use_cases.execute_dataset_use_case import ExecuteDatasetUseCase
from src.infrastructure.aws.dynamodb_client import DynamoDbClient
from src.infrastructure.aws.s3_client import S3Client
from src.infrastructure.aws.secrets_manager_client import SecretsManagerClient
from src.infrastructure.dynamodb.dataset_repository_impl import DatasetRepositoryImpl
from src.infrastructure.dynamodb.integration_repository_impl import IntegrationRepositoryImpl
from src.infrastructure.secrets.secrets_manager_provider import SecretsManagerProvider
from src.infrastructure.sftp.paramiko_sftp_client import ParamikoSftpClient
from src.infrastructure.s3.s3_storage_client import S3StorageClient
from src.infrastructure.s3.s3_metadata_repository import S3MetadataRepository


dynamodb = DynamoDbClient()
s3 = S3Client()

dataset_repository = DatasetRepositoryImpl(
    dynamodb_client=dynamodb,
    table_name=os.getenv("DATASET_TABLE", "sftp_delivery_dataset"),
)
integration_repository = IntegrationRepositoryImpl(
    dynamodb_client=dynamodb,
    table_name=os.getenv("INTEGRATION_TABLE", "sftp_delivery_integration"),
)
secret_provider = SecretsManagerProvider(SecretsManagerClient())
sftp_client = ParamikoSftpClient()
storage_client = S3StorageClient(s3_client=s3)
metadata_repository = S3MetadataRepository(
    s3_client=s3,
    bucket_name=os.environ["METADATA_BUCKET"],
    metadata_prefix=os.getenv("METADATA_PREFIX", "BRONZE"),
)

request = ExecutionRequest(
    integration=os.getenv("INTEGRATION", "compartamos_sftp"),
    dataset=os.getenv("DATASET", "transaction"),
    start_date=date.fromisoformat(os.environ["START_DATE"])
    if os.getenv("START_DATE") else None,
    end_date=date.fromisoformat(os.environ["END_DATE"])
    if os.getenv("END_DATE") else None,
)

response = ExecuteDatasetUseCase(
    dataset_repository,
    integration_repository,
    secret_provider,
    sftp_client,
    storage_client,
    metadata_repository,
).execute(request)

print(response)
