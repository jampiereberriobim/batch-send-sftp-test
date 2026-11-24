from src.application.dto.execution_request import ExecutionRequest
from src.application.dto.execution_response import ExecutionResponse
from datetime import datetime, timedelta, date
from src.domain.entities.dataset import Dataset
from src.domain.entities.integration import Integration
from src.domain.entities.remote_file import RemoteFile
from src.domain.entities.sftp_credentials import SftpCredentials

from src.domain.ports.dataset_repository import DatasetRepository
from src.domain.ports.integration_repository import IntegrationRepository
from src.domain.ports.secret_provider import SecretProvider
from src.domain.ports.sftp_client import SftpClient
from src.domain.ports.storage_client import StorageClient
from src.domain.ports.metadata_repository import MetadataRepository
from src.shared.logger import logger
import uuid
from datetime import datetime


class ExecuteDatasetUseCase:

    def __init__(
        self,
        dataset_repository: DatasetRepository,
        integration_repository: IntegrationRepository,
        secret_provider: SecretProvider,
        sftp_client: SftpClient,
        storage_client: StorageClient,
        metadata_repository: MetadataRepository,
    ) -> None:

        self._dataset_repository = dataset_repository
        self._integration_repository = integration_repository
        self._secret_provider = secret_provider
        self._sftp_client = sftp_client
        self._storage_client = storage_client
        self._metadata_repository = metadata_repository

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResponse:

        logger.info("Starting execution")

        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        uploaded_files = 0
        processed_files = 0

        status = "SUCCESS"
        error_message = None

        try:

            logger.info(
                "Integration=%s Dataset=%s",
                request.integration,
                request.dataset,
            )

            dataset = self._load_dataset(request)

            integration = self._load_integration(dataset)

            credentials = self._load_credentials(integration)
            
            self._connect(credentials)            
            
            prefixes = self._resolve_prefixes(
                request,
                dataset,
            )
            
            for prefix in prefixes:
            
                files = self._list_files(prefix)

                processed_files += len(files)

                transferred_files += self._process_files(
                    files,
                    dataset,
                )

            self._disconnect()

            return ExecutionResponse(
                integration=request.integration,
                dataset=request.dataset,
                processed_files=processed_files,
                uploaded_files=transferred_files,
                success=True,
                message="Execution completed successfully.",
            )

        except Exception as e:

            status = "ERROR"
            error_message = str(e)

            logger.exception(error_message)

            raise

        finally:

            end_time = datetime.utcnow()

            execution_time = (
                end_time - start_time
            ).total_seconds()

            self._generate_metadata(
                execution_id=execution_id,
                request=request,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                processed_files=processed_files,
                uploaded_files=uploaded_files,
                status=status,
                error_message=error_message,
            )

    def _resolve_prefixes(
        self,
        request: ExecutionRequest,
        dataset: Dataset,
    ) -> list[str]:
    
        if "{date}" not in dataset.source_prefix:
            return [dataset.source_prefix]
    
        start_date = request.start_date or date.today()
        end_date = request.end_date or start_date
    
        prefixes = []
    
        current = start_date
    
        while current <= end_date:
        
            prefixes.append(
                dataset.source_prefix.replace(
                    "{date}",
                    current.strftime("%Y-%m-%d"),
                )
            )
    
            current += timedelta(days=1)
    
        return prefixes

    def _load_dataset(
        self,
        request: ExecutionRequest,
    ) -> Dataset:

        return self._dataset_repository.get(
            integration=request.integration,
            dataset=request.dataset,
        )

    def _load_integration(
        self,
        dataset: Dataset,
    ) -> Integration:

        return self._integration_repository.get(
            dataset.integration
        )

    def _load_credentials(
        self,
        integration: Integration,
    ) -> SftpCredentials:

        return self._secret_provider.get_secret(
            integration.secret_name
        )

    def _connect(
        self,
        credentials: SftpCredentials,
    ) -> None:

        self._sftp_client.connect(credentials)

    def _disconnect(
        self,
    ) -> None:

        self._sftp_client.disconnect()

    def _list_files(
        self,
        dataset: Dataset,
    ) -> list[RemoteFile]:

        return self._sftp_client.list_files(
            remote_path=dataset.remote_path,
            pattern=dataset.file_pattern,
            recursive=dataset.recursive,
        )

    def _process_files(
        self,
        files: list[RemoteFile],
        dataset: Dataset,
    ) -> int:

        uploaded = 0

        for remote_file in files:

            stream = self._sftp_client.download(
                remote_file
            )

            self._storage_client.upload(
                file_stream=stream,
                remote_file=remote_file,
                integration=dataset.integration,
                destination_prefix=dataset.destination_prefix,
            )

            uploaded += 1

        return uploaded

    def _generate_metadata(
        self,
        execution_id: str,
        request: ExecutionRequest,
        start_time: datetime,
        end_time: datetime,
        execution_time: float,
        processed_files: int,
        uploaded_files: int,
        status: str,
        error_message: str | None,
    ) -> None:

        metadata = {
            "execution_id": execution_id,
            "integration": request.integration,
            "dataset": request.dataset,
            "report_name": request.dataset,
            "processed_date": start_time.date().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "sent_time_utc": end_time.isoformat(),
            "processed_files": processed_files,
            "uploaded_files": uploaded_files,
            "status": status,
            "error_message": error_message,
            "execution_time": execution_time,
        }

        self._metadata_repository.save(metadata)
        
        
