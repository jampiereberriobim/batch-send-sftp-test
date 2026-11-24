from src.domain.entities.integration import Integration
from src.domain.exceptions.integration_not_found import (
    IntegrationNotFound,
)
from src.domain.ports.integration_repository import (
    IntegrationRepository,
)

from src.infrastructure.aws.dynamodb_client import DynamoDbClient


class IntegrationRepositoryImpl(
    IntegrationRepository
):
    """
    DynamoDB implementation of IntegrationRepository.
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
    ) -> Integration:

        response = self._table.get_item(
            Key={
                "integration": integration,
            }
        )

        item = response.get("Item")

        if item is None:
            raise IntegrationNotFound(
                f"Integration '{integration}' not found."
            )

        return Integration(
            name=item["integration"],
            secret_name=item["secret_name"],
            enabled=item["enabled"],
            description=item.get("description"),
        )