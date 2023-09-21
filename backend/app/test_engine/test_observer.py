from abc import abstractmethod
from typing import List, Protocol


class Observer(Protocol):
    @abstractmethod
    def dispatch(self, observable) -> None:  # type: ignore
        """Receive Notifications"""


class Observable(Protocol):
    @abstractmethod
    def subscribe(self, observers: List[Observer]) -> None:
        """The subscribe method"""

    @abstractmethod
    def unsubscribe(self, observers: List[Observer]) -> None:
        """The unsubscribe observer method"""

    @abstractmethod
    def notify(self) -> None:
        """The notify method"""
