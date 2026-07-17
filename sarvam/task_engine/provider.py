from abc import ABC, abstractmethod


class TaskProvider(ABC):
    @abstractmethod
    def execute(self, task: str, context: dict) -> str:
        ...
