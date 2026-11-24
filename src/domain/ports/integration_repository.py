from abc import ABC, abstractmethod

from src.domain.entities.integration import Integration


class IntegrationRepository(ABC):
    """
    Contract for retrieving integration configurations.
    """

    @abstractmethod
    def get(self, integration: str) -> Integration:
        """
        Retrieves an integration configuration.

        Args:
            integration: Integration name.

        Returns:
            Integration configuration.
        """
        pass