"""Task graph schema shared by every planner backend."""
import json
from dataclasses import asdict, dataclass, field

# The only actions a robot adapter is expected to understand.
VOCABULARY = ("navigate_to", "pickup", "place", "inspect", "wait", "speak")


@dataclass
class TaskNode:
    id: str
    action: str
    target: str = ""
    params: dict = field(default_factory=dict)


@dataclass
class TaskGraph:
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)  # [(from_id, to_id), ...]

    def to_json(self) -> str:
        return json.dumps({
            "nodes": [asdict(n) for n in self.nodes],
            "edges": [list(e) for e in self.edges],
        })

    @classmethod
    def from_json(cls, raw: str) -> "TaskGraph":
        doc = json.loads(raw)
        return cls(
            nodes=[TaskNode(**n) for n in doc.get("nodes", [])],
            edges=[tuple(e) for e in doc.get("edges", [])],
        )

    def sequential(self) -> list:
        """Nodes in execution order (this planner only emits linear graphs)."""
        return list(self.nodes)
