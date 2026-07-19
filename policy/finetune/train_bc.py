"""Behaviour cloning for the navigation policy.

Deliberately a linear policy fitted by ridge regression, not a deep net: the blueprint's
warm-start requirement (section 11.3) is "pretrained baseline, never random init", and a
closed-form fit trains in milliseconds on a laptop with no GPU. It is also trivially
quantizable, which is what the Hexagon export path needs.
"""
import numpy as np


class LinearPolicy:
    """action = W @ obs + b."""

    def __init__(self, W, b):
        self.W = np.asarray(W, dtype=np.float64)
        self.b = np.asarray(b, dtype=np.float64)

    @property
    def obs_dim(self) -> int:
        return self.W.shape[1]

    @property
    def act_dim(self) -> int:
        return self.W.shape[0]

    def act(self, obs):
        return self.W @ np.asarray(obs, dtype=np.float64) + self.b

    def save(self, path: str) -> str:
        np.savez(path, W=self.W, b=self.b)
        return path

    @classmethod
    def load(cls, path: str) -> "LinearPolicy":
        with np.load(path) as npz:
            return cls(npz["W"], npz["b"])

    def quantize_int8(self) -> dict:
        """Per-tensor symmetric int8 quantization; the export path's payload."""
        out = {}
        for name, tensor in (("W", self.W), ("b", self.b)):
            peak = float(np.abs(tensor).max())
            scale = (peak / 127.0) if peak > 0 else 1.0
            out[name] = {
                "data": np.clip(np.round(tensor / scale), -127, 127).astype(np.int8),
                "scale": scale,
            }
        return out


def dequantize_int8(bundle: dict) -> "LinearPolicy":
    """Inverse of quantize_int8 — what the on-device runtime reconstructs."""
    return LinearPolicy(
        bundle["W"]["data"].astype(np.float64) * bundle["W"]["scale"],
        bundle["b"]["data"].astype(np.float64) * bundle["b"]["scale"],
    )


def make_baseline(obs_dim: int, act_dim: int) -> LinearPolicy:
    """Zero policy — the untrained starting point, and the control in evaluation."""
    return LinearPolicy(np.zeros((act_dim, obs_dim)), np.zeros(act_dim))


def finetune_bc(policy: LinearPolicy, demos, l2: float = 1e-3) -> LinearPolicy:
    """Ridge-regress (obs -> action) over demonstration pairs.

    demos: iterable of (obs, action) pairs, or of {"obs": [...], "actions": [...]}.
    """
    obs, actions = [], []
    for demo in demos:
        if isinstance(demo, dict):
            obs.extend(demo["obs"])
            actions.extend(demo["actions"])
        else:
            o, a = demo
            obs.append(o)
            actions.append(a)

    if not obs:
        return policy  # nothing to learn from; keep the warm start

    X = np.asarray(obs, dtype=np.float64)
    Y = np.asarray(actions, dtype=np.float64)
    X1 = np.hstack([X, np.ones((len(X), 1))])  # bias as an extra column

    # (X'X + l2 I)^-1 X'Y
    gram = X1.T @ X1 + l2 * np.eye(X1.shape[1])
    theta = np.linalg.solve(gram, X1.T @ Y)  # (obs_dim + 1, act_dim)
    return LinearPolicy(theta[:-1].T, theta[-1])
