from datetime import date, datetime, timedelta
import uuid

from src.application.dto.execution_request import ExecutionRequest
from src.application.dto.execution_response import ExecutionResponse
from src.domain.entities.dataset import Dataset
from src.domain.entities.integration import Integration
from src.domain.entities.sftp_credentials import SftpCredentials
from src.domain.ports.dataset_repository import DatasetRepository
from src.domain.ports.integration_repository import IntegrationRepository
from src.domain.ports.metadata_repository import MetadataRepository
from src.domain.ports.secret_provider import SecretProvider
from src.domain.ports.sftp_client import SftpClient
from src.domain.ports.storage_client import StorageClient
from src.shared.logger import logger


class ExecuteDatasetUseCase:
    """Coordinates the S3-to-SFTP transfer workflow."""

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

    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        logger.info("Starting S3-to-SFTP execution")
        logger.info(
            "Integration=%s Dataset=%s",
            request.integration,
            request.dataset,
        )

        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        processed_files = 0
        uploaded_files = 0
        status = "ERROR"
        error_message = None
        connected = False

        try:
            dataset = self._dataset_repository.get(
                integration=request.integration,
                dataset=request.dataset,
            )
            if not dataset.enabled:
                raise ValueError(
                    f"Dataset '{request.dataset}' is disabled."
                )

            integration = self._load_integration(dataset)
            if not integration.enabled:
                raise ValueError(
                    f"Integration '{integration.name}' is disabled."
                )

            credentials = self._secret_provider.get_secret(
                integration.secret_name
            )
            self._sftp_client.connect(credentials)
            connected = True

            prefixes = self._resolve_prefixes(request, dataset)
            for prefix in prefixes:
                files = self._storage_client.list_files(
                    bucket_name=dataset.source_bucket,
                    prefix=prefix,
                    recursive=dataset.recursive,
                )
                logger.info(
                    "Found %s files in s3://%s/%s",
                    len(files),
                    dataset.source_bucket,
                    prefix,
                )
                processed_files += len(files)

                for source_file in files:
                    source_stream = self._storage_client.download(
                        source_file,
                        bucket_name=dataset.source_bucket,
                    )
                    self._sftp_client.upload(
                        file_stream=source_stream,
                        remote_path=dataset.remote_path,
                        filename=source_file.name,
                    )
                    uploaded_files += 1

            status = "SUCCESS"
            return ExecutionResponse(
                integration=request.integration,
                dataset=request.dataset,
                processed_files=processed_files,
                uploaded_files=uploaded_files,
                success=True,
                message="Execution completed successfully.",
            )
        except Exception as exc:
            error_message = str(exc)
            logger.exception("Dataset execution failed: %s", error_message)
            raise
        finally:
            if connected:
                try:
                    self._sftp_client.disconnect()
                except Exception:
                    logger.exception("Failed to close SFTP connection.")

            end_time = datetime.utcnow()
            self._generate_metadata(
                execution_id=execution_id,
                request=request,
                start_time=start_time,
                end_time=end_time,
                execution_time=(end_time - start_time).total_seconds(),
                processed_files=processed_files,
                uploaded_files=uploaded_files,
                status=status,
                error_message=error_message,
            )

    def _load_integration(self, dataset: Dataset) -> Integration:
        return self._integration_repository.get(dataset.integration)

    @staticmethod
    def _format_date_template(template: str, execution_date: date) -> str:
        replacements = {
            "{date}": execution_date.strftime("%Y-%m-%d"),
            "{yyyy}": execution_date.strftime("%Y"),
            "{MM}": execution_date.strftime("%m"),
            "{dd}": execution_date.strftime("%d"),
            "{yyyyMMdd}": execution_date.strftime("%Y%m%d"),
        }
        result = template
        for token, value in replacements.items():
            result = result.replace(token, value)
        return result

    def _resolve_prefixes(
        self,
        request: ExecutionRequest,
        dataset: Dataset,
    ) -> list[str]:
        template = dataset.date_template or ""
        has_date_token = any(
            token in template
            for token in ("{date}", "{yyyy}", "{MM}", "{dd}", "{yyyyMMdd}")
        )

        if not has_date_token:
            return [
                f"{dataset.source_prefix.rstrip('/')}/"
                f"{template.strip('/')}".strip("/")
            ]

        start_date = request.start_date or date.today()
        end_date = request.end_date or start_date
        if end_date < start_date:
            raise ValueError("end_date cannot be earlier than start_date.")

        prefixes = []
        current = start_date
        while current <= end_date:
            rendered_template = self._format_date_template(
                template,
                current,
            ).strip("/")
            prefix_parts = [
                dataset.source_prefix.strip("/"),
                rendered_template,
            ]
            prefixes.append(
                "/".join(part for part in prefix_parts if part) + "/"
            )
            current += timedelta(days=1)

        return prefixes

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
