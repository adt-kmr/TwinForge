from abc import ABC, abstractmethod


class TwinForgeRobot(ABC):
    @abstractmethod
    def move(self, x: float, y: float, theta: float):
        ...

    @abstractmethod
    def capture_frame(self) -> bytes:
        ...

    @abstractmethod
    def get_pose(self) -> tuple:
        ...
