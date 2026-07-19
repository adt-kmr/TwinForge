"""Ingest point-cloud/mesh exports from the Scaniverse app into TwinForge's PLY pipeline.

Scaniverse (phone-side capture tool, external to TwinForge) exports either:
- `.ply` point clouds — already TwinForge's native format, ingested directly.
- `.glb` meshes — not yet supported (see ingest_export).
"""
import os
import shutil

from reconstruction.reconstruct import read_ply


def ingest_export(path: str, scan_dir: str) -> dict:
    """Copy a Scaniverse export into scan_dir as a TwinForge-native PLY.

    Args:
        path: Path to the Scaniverse export file (.ply or .glb).
        scan_dir: Destination scan directory.

    Returns:
        Dict with keys: ply_path, point_count, source.

    Raises:
        NotImplementedError: For .glb exports (mesh import not yet supported).
        ValueError: For any other unrecognized extension.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".glb":
        raise NotImplementedError("glb import not yet supported; export PLY from Scaniverse")

    if ext != ".ply":
        raise ValueError(f"unsupported Scaniverse export type: {ext}")

    os.makedirs(scan_dir, exist_ok=True)
    dest_path = os.path.join(scan_dir, "scaniverse.ply")
    shutil.copyfile(path, dest_path)

    points, _colors = read_ply(dest_path)
    return {"ply_path": dest_path, "point_count": len(points), "source": "scaniverse"}
