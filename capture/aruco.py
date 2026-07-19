"""ArUco marker detection for camera pose estimation.

Provides marker detection using cv2.aruco (lazy-imported) and transformation
matrix composition from rotation and translation vectors.
"""

import numpy as np
from typing import Optional, Dict, Any

# Physical marker size in meters
MARKER_SIZE_M = 0.15


def compose_transform(rvec, tvec) -> list[list[float]]:
    """Convert rotation and translation vectors to a 4x4 homogeneous transformation matrix.

    Uses manual Rodrigues formula to work without cv2.

    Args:
        rvec: Rotation vector (3,) in axis-angle representation.
        tvec: Translation vector (3,).

    Returns:
        4x4 transformation matrix as nested list (camera -> marker frame).
    """
    rvec = np.asarray(rvec, dtype=np.float64).flatten()
    tvec = np.asarray(tvec, dtype=np.float64).flatten()

    # Rodrigues formula: convert rotation vector to rotation matrix
    theta = np.linalg.norm(rvec)

    if theta < 1e-10:
        # Near-zero rotation: use identity
        R = np.eye(3)
    else:
        # Normalized rotation axis
        v = rvec / theta

        # Skew-symmetric matrix (cross-product operator)
        v_x = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

        # Rodrigues formula: R = I + sin(θ)[v]_x + (1-cos(θ))[v]_x^2
        R = np.eye(3) + np.sin(theta) * v_x + (1 - np.cos(theta)) * (v_x @ v_x)

    # Construct 4x4 homogeneous transformation matrix
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = tvec

    # Return as nested list
    return T.tolist()


def detect_marker(
    image_path: str, marker_id: int = 0, camera_intrinsics: Optional[np.ndarray] = None
) -> Optional[Dict[str, Any]]:
    """Detect an ArUco marker in an image and estimate camera pose relative to marker.

    Uses cv2.aruco with DICT_4X4_50 dictionary.

    Args:
        image_path: Path to the image file.
        marker_id: ID of the marker to detect (default: 0).
        camera_intrinsics: Camera intrinsic matrix (3x3). If None, uses a default.

    Returns:
        Dict with keys: marker_id, rvec, tvec, transform (4x4 matrix).
        Returns None if marker not found.

    Raises:
        RuntimeError: If cv2 is not installed.
    """
    try:
        import cv2
    except ImportError:
        raise RuntimeError("opencv-python not installed; install the 'vision' extra")

    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create ArUco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(aruco_dict)

    # Detect markers
    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is None or marker_id not in ids.flatten():
        return None

    # Find the marker we're looking for
    idx = np.where(ids.flatten() == marker_id)[0][0]
    marker_corners = corners[idx]

    # Set up camera intrinsics (default: assumes 640x480 image with reasonable FOV)
    if camera_intrinsics is None:
        h, w = gray.shape
        # Default: focal length based on image size, principal point at center
        fx = w
        fy = h
        cx = w / 2
        cy = h / 2
        camera_intrinsics = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
    else:
        camera_intrinsics = np.asarray(camera_intrinsics, dtype=np.float32)

    # Estimate pose using cv2.solvePnP
    # Marker corners in 3D (z=0 on the marker plane, centered)
    half_size = MARKER_SIZE_M / 2
    marker_3d = np.array(
        [
            [-half_size, -half_size, 0],
            [half_size, -half_size, 0],
            [half_size, half_size, 0],
            [-half_size, half_size, 0],
        ],
        dtype=np.float32,
    )

    # Marker corners in 2D (image plane)
    marker_2d = marker_corners[0].astype(np.float32)

    # Solve for pose
    success, rvec, tvec = cv2.solvePnP(
        marker_3d,
        marker_2d,
        camera_intrinsics,
        None,
        useExtrinsicGuess=False,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return None

    # Convert to Python lists for JSON serialization
    rvec = rvec.flatten().tolist()
    tvec = tvec.flatten().tolist()

    # Compute 4x4 transformation matrix
    transform = compose_transform(rvec, tvec)

    return {
        "marker_id": int(marker_id),
        "rvec": rvec,
        "tvec": tvec,
        "transform": transform,
    }
