from abc import ABC, abstractmethod


class NotificationRepository(ABC):
    """Port for persisting process completion notifications."""

    @abstractmethod
    def save(self, notification: dict) -> None:
        pass
