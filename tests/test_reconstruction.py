import numpy as np
import pytest

from reconstruction.fast_path.fusion import fuse_frames
from reconstruction.reconstruct import read_ply, reconstruct

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
