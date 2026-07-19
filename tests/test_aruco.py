import pytest
import numpy as np
import tempfile
from pathlib import Path

from capture.aruco import compose_transform, detect_marker, MARKER_SIZE_M


def test_compose_transform_creates_4x4_homogeneous_matrix():
    """Test that compose_transform creates a valid 4x4 homogeneous transformation matrix."""
    # Use a known rvec and tvec for testing
    # rvec = [0, 0, 0] (identity rotation), tvec = [1, 2, 3]
    rvec = np.array([0.0, 0.0, 0.0])
    tvec = np.array([1.0, 2.0, 3.0])

    transform = compose_transform(rvec, tvec)

    # Should be a 4x4 matrix
    assert len(transform) == 4
    assert all(len(row) == 4 for row in transform)

    # Convert to numpy for easier checking
    T = np.array(transform)

    # Last row should be [0, 0, 0, 1]
    np.testing.assert_array_almost_equal(T[3], [0, 0, 0, 1])

    # For identity rotation (rvec=[0,0,0]), rotation part should be identity
    R = T[:3, :3]
    np.testing.assert_array_almost_equal(R, np.eye(3), decimal=5)

    # Translation should match tvec
    t = T[:3, 3]
    np.testing.assert_array_almost_equal(t, [1.0, 2.0, 3.0], decimal=5)


def test_compose_transform_produces_orthonormal_rotation():
    """Test that the rotation matrix R satisfies R @ R.T ≈ I (orthonormality)."""
    # Create a small rotation: 45 degrees around z-axis
    theta = np.pi / 4  # 45 degrees
    rvec = np.array([0.0, 0.0, theta])  # rotation around z
    tvec = np.array([0.5, 0.5, 2.0])

    transform = compose_transform(rvec, tvec)
    T = np.array(transform)

    R = T[:3, :3]

    # R @ R.T should be identity (orthonormality check)
    orthogonal_check = R @ R.T
    np.testing.assert_array_almost_equal(orthogonal_check, np.eye(3), decimal=5)

    # det(R) should be 1 (proper rotation, not reflection)
    det_R = np.linalg.det(R)
    np.testing.assert_almost_equal(det_R, 1.0, decimal=5)


def test_compose_transform_works_with_non_zero_rotation():
    """Test compose_transform with non-zero rotation vectors."""
    # 90 degrees rotation around x-axis
    rvec = np.array([np.pi / 2, 0.0, 0.0])
    tvec = np.array([0.0, 1.0, 2.0])

    transform = compose_transform(rvec, tvec)
    T = np.array(transform)

    # Should still be a valid 4x4 matrix
    assert T.shape == (4, 4)

    # Last row should be [0, 0, 0, 1]
    np.testing.assert_array_almost_equal(T[3], [0, 0, 0, 1])

    # Rotation part should be orthonormal
    R = T[:3, :3]
    np.testing.assert_array_almost_equal(R @ R.T, np.eye(3), decimal=5)


def test_detect_marker_finds_generated_marker():
    """Real round-trip: generate a marker image, detect it for real (no mocking cv2)."""
    cv2 = pytest.importorskip("cv2")

    marker_id = 0

    # Generate a real marker image
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, 300, borderBits=1)

    # Pad with a white quiet zone -- ArUco detection needs margin around the marker
    # to find the border, so a bare marker with no surrounding whitespace won't detect.
    padded = cv2.copyMakeBorder(marker_image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)

    # Create a test image with the marker
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        temp_path = f.name
        cv2.imwrite(temp_path, padded)

    try:
        # Call detect_marker for real -- default camera intrinsics (derived from
        # image size inside detect_marker) are a plausible enough pinhole model.
        result = detect_marker(temp_path, marker_id=marker_id)

        # Should find the marker
        assert result is not None

        # Check required keys
        assert "marker_id" in result
        assert "rvec" in result
        assert "tvec" in result
        assert "transform" in result

        # Marker ID should match
        assert result["marker_id"] == marker_id

        # tvec should be a list/array of 3 elements
        assert len(result["tvec"]) == 3

        # tvec z-component should be positive (marker in front of camera)
        assert result["tvec"][2] > 0

        # transform should be 4x4
        transform = result["transform"]
        assert len(transform) == 4
        assert all(len(row) == 4 for row in transform)

        # transform should be a valid homogeneous matrix
        T = np.array(transform)
        # Last row should be [0, 0, 0, 1]
        np.testing.assert_array_almost_equal(T[3], [0, 0, 0, 1])
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


def test_marker_size_m_constant_is_defined():
    """Test that MARKER_SIZE_M constant is defined and has expected value."""
    assert MARKER_SIZE_M == 0.15
    assert isinstance(MARKER_SIZE_M, (int, float))


def test_detect_marker_raises_error_without_opencv(mocker):
    """Test that detect_marker raises RuntimeError when cv2 is not available.

    Forces the lazy `import cv2` inside detect_marker to fail regardless of whether
    opencv-python happens to be installed in the current environment, by making
    cv2 resolve to None in sys.modules (the standard way to simulate a missing
    module without needing to actually uninstall it).
    """
    mocker.patch.dict("sys.modules", {"cv2": None})

    with pytest.raises(RuntimeError, match="opencv-python not installed"):
        detect_marker("dummy_path.png", marker_id=0)
