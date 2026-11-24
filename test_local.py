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


dataset_repository = DatasetRepositoryImpl(
    dynamodb_client=DynamoDbClient(),
    table_name="sftp_delivery_dataset"
)

integration_repository = IntegrationRepositoryImpl(
    dynamodb_client=DynamoDbClient(),
    table_name="sftp_delivery_integration"
)

secret_provider = SecretsManagerProvider(
    SecretsManagerClient()
)

sftp_client = ParamikoSftpClient()

storage_client = S3StorageClient(
    S3Client(),
    "uat-temp-992382450203"
)

metadata_repository = S3MetadataRepository(
    S3Client(),
    "uat-temp-992382450203",
    "BRONZE"
)

use_case = ExecuteDatasetUseCase(
    dataset_repository,
    integration_repository,
    secret_provider,
    sftp_client,
    storage_client,
    metadata_repository
)

request = ExecutionRequest(
    integration="compartamos_sftp",
    dataset="transaction"
)

response = use_case.execute(request)

print(response)