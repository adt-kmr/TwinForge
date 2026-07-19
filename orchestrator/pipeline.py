from enum import Enum


class PipelineState(Enum):
    CAPTURE = "capture"
    RECONSTRUCT = "reconstruct"
    SEMANTIC = "semantic"
    TWIN_GENERATE = "twin_generate"
    PLAN = "plan"
    TRAIN = "train"
    OPTIMIZE = "optimize"
    DEPLOY = "deploy"


# Execution order; a stage's index here is its position in the pipeline.
ORDER = tuple(PipelineState)


class Pipeline:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = PipelineState.CAPTURE
        self.jobs: list = []

    def transition(self, next_state: PipelineState) -> PipelineState:
        """Advance the pipeline. Forward-only: you may skip ahead but never back.

        Going backwards would let a later stage's artifacts silently outlive the
        earlier stage they were derived from, so it is refused rather than logged.
        """
        if ORDER.index(next_state) <= ORDER.index(self.state):
            raise ValueError(
                f"cannot transition {self.state.value} -> {next_state.value}; "
                "pipeline stages only move forward (start a new session to redo a stage)"
            )
        self.state = next_state
        self.jobs.append(next_state.value)
        return self.state
