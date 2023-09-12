from typing import List, Set

from app.test_engine.test_observer import Observable, Observer


class TestObservable(Observable):
    __test__ = False

    def __init__(self) -> None:
        self.observers: Set[Observer] = set()

    def subscribe(self, observers: List[Observer]) -> None:
        self.observers.update(observers)

    def unsubscribe(self, observers: List[Observer]) -> None:
        self.observers.difference_update(observers)

    def notify(self) -> None:
        for observer in self.observers:
            observer.dispatch(self)
