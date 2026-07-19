import numpy as np
import pytest

from capture.scaniverse import ingest_export
from reconstruction.reconstruct import write_ply


def test_ingest_ply_copies_and_counts_points(tmp_path):
    points = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])
    colors = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
    src = write_ply(str(tmp_path / "export.ply"), points, colors)

    scan_dir = tmp_path / "scan"
    scan_dir.mkdir()
    result = ingest_export(src, str(scan_dir))

    expected_path = str(scan_dir / "scaniverse.ply")
    assert result == {
        "ply_path": expected_path,
        "point_count": 3,
        "source": "scaniverse",
    }
    assert (scan_dir / "scaniverse.ply").exists()


def test_ingest_glb_not_implemented(tmp_path):
    src = tmp_path / "export.glb"
    src.write_bytes(b"glTF")

    with pytest.raises(NotImplementedError, match="glb import not yet supported"):
        ingest_export(str(src), str(tmp_path / "scan"))
