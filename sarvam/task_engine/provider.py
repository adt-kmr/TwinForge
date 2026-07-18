import os
from abc import ABC, abstractmethod


class TaskPlanner(ABC):
    """Natural language -> TaskGraph."""

    @abstractmethod
    def plan(self, text: str, lang: str = "en"):
        ...


class TaskProvider(ABC):
    """Older single-shot interface, kept for back-compat with existing callers."""

    @abstractmethod
    def execute(self, task: str, context: dict) -> str:
        ...


def get_planner(objects=None) -> TaskPlanner:
    """Sarvam when an API key is configured, on-device grammar otherwise."""
    from .fallback import FunctionGemmaPlanner
    from .sarvam_provider import SarvamPlanner

    if os.environ.get("SARVAM_API_KEY"):
        return SarvamPlanner(objects)
    return FunctionGemmaPlanner(objects)
