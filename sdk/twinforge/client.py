from .capture import capture
from .reconstruct import reconstruct
from .train import train
from .deploy import deploy


class TwinForge:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def capture(self, session_id: str) -> str:
        return capture(self.base_url, session_id)

    def reconstruct(self, session_id: str, method: str = "fast") -> str:
        return reconstruct(self.base_url, session_id, method)

    def train(self, config_path: str) -> str:
        return train(self.base_url, config_path)

    def deploy(self, model_id: str, target: str) -> str:
        return deploy(self.base_url, model_id, target)
