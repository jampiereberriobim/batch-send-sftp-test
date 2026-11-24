from abc import ABC, abstractmethod

from src.domain.entities.execution_metadata import ExecutionMetadata


class MetadataRepository(ABC):

    @abstractmethod
    def save(self, metadata: ExecutionMetadata) -> None:
        pass