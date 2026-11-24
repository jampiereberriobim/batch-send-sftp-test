from src.domain.entities.dataset import Dataset
from src.domain.exceptions.dataset_not_found import DatasetNotFound
from src.domain.ports.dataset_repository import DatasetRepository
from src.infrastructure.aws.dynamodb_client import DynamoDbClient


class DatasetRepositoryImpl(DatasetRepository):
    """DynamoDB implementation of DatasetRepository."""

    def __init__(
        self,
        dynamodb_client: DynamoDbClient,
        table_name: str,
    ) -> None:
        self._table = dynamodb_client.resource.Table(table_name)

    def get(self, integration: str, dataset: str) -> Dataset:
        response = self._table.get_item(
            Key={"integration": integration, "dataset": dataset}
        )
        item = response.get("Item")

        if item is None:
            raise DatasetNotFound(
                f"Dataset '{integration}/{dataset}' not found."
            )

        return Dataset(
            integration=item["integration"],
            name=item["dataset"],
            source_bucket=item["source_bucket"],
            source_prefix=item.get("source_prefix", ""),
            remote_path=item["remote_path"],
            enabled=item["enabled"],
            source_date_template=item.get("source_date_template", ""),
            source_suffix=item.get("source_suffix", ""),
            destination_date_template=item.get(
                "destination_date_template", ""
            ),
            recursive=item.get("recursive", False),
        )
