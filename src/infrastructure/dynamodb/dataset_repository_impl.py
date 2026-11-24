from boto3.resources.base import ServiceResource

from src.domain.entities.dataset import Dataset
from src.domain.exceptions.dataset_not_found import DatasetNotFound
from src.domain.ports.dataset_repository import DatasetRepository

from src.infrastructure.aws.dynamodb_client import DynamoDbClient


class DatasetRepositoryImpl(DatasetRepository):
    """
    DynamoDB implementation of DatasetRepository.
    """

    def __init__(
        self,
        dynamodb_client: DynamoDbClient,
        table_name: str,
    ) -> None:

        self._table = (
            dynamodb_client.resource.Table(table_name)
        )

    def get(
        self,
        integration: str,
        dataset: str,
    ) -> Dataset:

        response = self._table.get_item(
            Key={
                "integration": integration,
                "dataset": dataset,
            }
        )

        item = response.get("Item")

        if item is None:
            raise DatasetNotFound(
                f"Dataset '{integration}/{dataset}' not found."
            )

        return Dataset(
            integration=item["integration"],
            name=item["dataset"],
            remote_path=item["remote_path"],
            file_pattern=item["file_pattern"],
            destination_bucket=item["destination_bucket"],
            destination_prefix=item["destination_prefix"],
            enabled=item["enabled"],
            recursive=item.get("recursive", False),
            archive_path=item.get("archive_path"),
            delete_after_download=item.get(
                "delete_after_download",
                False,
            ),
        )