from .base import TwinForgeRobot


class SimRobot(TwinForgeRobot):
    def move(self, x: float, y: float, theta: float):
        pass

    def capture_frame(self) -> bytes:
        return b"sim_frame"

    def get_pose(self) -> tuple:
        return (0.0, 0.0, 0.0)
