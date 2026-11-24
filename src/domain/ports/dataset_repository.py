from abc import ABC, abstractmethod

from src.domain.entities.dataset import Dataset


class DatasetRepository(ABC):
    """
    Contract for retrieving dataset configurations.
    """

    @abstractmethod
    def get(
        self,
        integration: str,
        dataset: str
    ) -> Dataset:
        """
        Retrieves a dataset configuration.

        Args:
            integration: Integration name.
            dataset: Dataset name.

        Returns:
            Dataset configuration.
        """
        pass