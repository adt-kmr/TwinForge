import os

import numpy as np
import pytest

from reconstruction.fast_path.fusion import fuse_frames
from reconstruction.reconstruct import read_ply, reconstruct, write_ply

K = np.array([[10.0, 0, 8.0], [0, 10.0, 8.0], [0, 0, 1.0]])


def flat_floor_frame(z=2.0):
    # camera looking straight down at a floor plane z metres away
    return {
        "depth": np.full((16, 16), z, dtype=np.float32),
        "intrinsics": K,
        "pose": np.eye(4),
        "color": np.full((16, 16, 3), 128, dtype=np.uint8),
    }


def test_fuse_frames_bounds_and_dedup():
    f = flat_floor_frame()
    single, _ = fuse_frames([f], voxel_size=0.02)
    double, _ = fuse_frames([f, f], voxel_size=0.02)
    assert len(double) == len(single)  # identical frame dedups away
    assert np.allclose(single[:, 2], 2.0)  # all points on the plane
    assert single[:, 0].min() >= -2.0 and single[:, 0].max() <= 2.0


def test_reconstruct_writes_ply(tmp_path):
    f = flat_floor_frame()
    np.savez(tmp_path / "frame_00000.npz", **f)
    result = reconstruct(str(tmp_path), mode="fast")
    assert result["point_count"] == 16 * 16
    points, colors = read_ply(result["ply_path"])
    assert len(points) == 16 * 16
    assert tuple(colors[0]) == (128, 128, 128)


def test_fidelity_requires_colmap(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "")
    with pytest.raises(RuntimeError, match="COLMAP"):
        reconstruct(str(tmp_path), mode="fidelity")


def test_empty_scan_raises(tmp_path):
    with pytest.raises(ValueError, match="no frame"):
        reconstruct(str(tmp_path), mode="fast")


def test_reconstruct_falls_back_to_scaniverse_ply(tmp_path):
    """A scan_dir with no frame_*.npz files but a scaniverse.ply (Scaniverse import,
    Task 5's capture/scaniverse.py) must still reconstruct rather than raising."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])
    colors = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
    write_ply(str(tmp_path / "scaniverse.ply"), points, colors)

    result = reconstruct(str(tmp_path), mode="fast")
    assert result["point_count"] == 3
    assert result["glb_path"] is None
    out_points, out_colors = read_ply(result["ply_path"])
    assert len(out_points) == 3
    assert tuple(out_colors[0]) == (255, 0, 0)


def test_reconstruct_scaniverse_fallback_writes_into_out_dir(tmp_path):
    """When out_dir differs from scan_dir, the fallback must still land its output
    under out_dir, matching the npz-fusion path's artifact-location convention."""
    scan_dir = tmp_path / "scan"
    scan_dir.mkdir()
    out_dir = tmp_path / "out"
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    colors = np.array([[10, 20, 30], [40, 50, 60]], dtype=np.uint8)
    write_ply(str(scan_dir / "scaniverse.ply"), points, colors)

    result = reconstruct(str(scan_dir), mode="fast", out_dir=str(out_dir))
    assert result["point_count"] == 2
    assert os.path.commonpath([result["ply_path"], str(out_dir)]) == str(out_dir)
