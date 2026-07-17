from enum import Enum


class PipelineState(Enum):
    CAPTURE = "capture"
    RECONSTRUCT = "reconstruct"
    SEMANTIC = "semantic"
    TWIN_GENERATE = "twin_generate"
    DEPLOY = "deploy"


class Pipeline:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = PipelineState.CAPTURE
        self.jobs = []

    def transition(self, next_state: PipelineState):
        self.state = next_state
