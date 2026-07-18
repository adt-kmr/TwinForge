"""Local QAIRT conversion — the fallback when AI Hub is unreachable.

Same bundle shape as the AI Hub path so the orchestrator does not care which ran.
"""
import os
import shutil

from deployment.aihub_export.export_script import DEFAULT_DEVICE, _write_bundle
from policy.finetune.train_bc import LinearPolicy


def convert_to_qairt(policy_path: str, out_dir: str | None = None,
                     device_label: str = DEFAULT_DEVICE) -> dict:
    policy = LinearPolicy.load(policy_path)
    out_dir = out_dir or os.path.join(os.path.dirname(policy_path) or ".", "qairt")
    backend = "qairt" if shutil.which("qairt-converter") else "local"
    return _write_bundle(policy, out_dir, device_label, backend=backend, fmt="qairt")
