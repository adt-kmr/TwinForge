"""Calibrate a camera-to-world homography from fixed ArUco markers.

The script detects the configured landmarks, fits a single homography,
and optionally exports a dense pixel-to-world map for downstream use.
"""

import cv2
import numpy as np
import json
import sys
from itertools import combinations, permutations, product

# Camera source can be:
# - int index for USB cam (0, 1, ...)
# - string URL for IP cam stream (e.g. "http://192.168.1.50:4747/video")
CAMERA_SOURCE = 3
CAMERA_NAME = "camA"
CAMERA_FRAME_WIDTH = 1920
CAMERA_FRAME_HEIGHT = 1080
EXPORT_DENSE_WORLD_MAP = True
MANUAL_ASSIGNMENT_MODE = False

# --- FILL THIS IN with your real measurements ---
# If you printed the SAME ID on all 3 markers, keep one key and provide
# 3 physical instances under it.
# Example:
# MARKERS = {
#     23: [
#         {"center_cm": (0.0, 0.0), "length_cm": 8.0},
#         {"center_cm": (75.0, 100.0), "length_cm": 8.0},
#         {"center_cm": (140.0, 204.0), "length_cm": 8.0},
#     ]
# }
MARKERS = {
    23: [
        {"center_cm": (0.0, 0.0), "length_cm": 8.0},
        {"center_cm": (75.0, 100.0), "length_cm": 8.0},
        {"center_cm": (140.0, 204.0), "length_cm": 8.0},
    ],
}
# --------------------------------------------------

STABILITY_FRAMES = 20  # consecutive good frames before auto-lock

ARUCO_DICT_CHOICES = [
    ("4x4_50", cv2.aruco.DICT_4X4_50),
    ("4x4_100", cv2.aruco.DICT_4X4_100),
    ("5x5_50", cv2.aruco.DICT_5X5_50),
    ("6x6_50", cv2.aruco.DICT_6X6_50),
    ("APRILTAG_36h11", cv2.aruco.DICT_APRILTAG_36h11),
]

DETECTOR_PARAMS = cv2.aruco.DetectorParameters()
DETECTOR_PARAMS.adaptiveThreshWinSizeMin = 3
DETECTOR_PARAMS.adaptiveThreshWinSizeMax = 53
DETECTOR_PARAMS.adaptiveThreshWinSizeStep = 4
DETECTOR_PARAMS.minMarkerPerimeterRate = 0.01
DETECTOR_PARAMS.maxMarkerPerimeterRate = 4.0
if hasattr(DETECTOR_PARAMS, "cornerRefinementMethod"):
    DETECTOR_PARAMS.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
if hasattr(DETECTOR_PARAMS, "cornerRefinementWinSize"):
    DETECTOR_PARAMS.cornerRefinementWinSize = 7
if hasattr(DETECTOR_PARAMS, "cornerRefinementMaxIterations"):
    DETECTOR_PARAMS.cornerRefinementMaxIterations = 50
if hasattr(DETECTOR_PARAMS, "cornerRefinementMinAccuracy"):
    DETECTOR_PARAMS.cornerRefinementMinAccuracy = 0.01
if hasattr(DETECTOR_PARAMS, "detectInvertedMarker"):
    DETECTOR_PARAMS.detectInvertedMarker = True

DETECTORS = [
    (name, cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(dict_id), DETECTOR_PARAMS))
    for name, dict_id in ARUCO_DICT_CHOICES
]


mouse_state = {"x": None, "y": None}
H_CURRENT = None
FRAME_SHAPE = None
selected_detection_idx = None
slot_to_detection_idx = {}


def open_camera(source):
    """Open either a local camera index or an IP stream URL."""
    if isinstance(source, int):
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap

    if isinstance(source, str):
        s = source.strip()
        if s.isdigit():
            cap = cv2.VideoCapture(int(s))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return cap

        cap = cv2.VideoCapture(s)
        # IP streams usually ignore width/height requests; the phone/app must
        # expose the higher resolution. We still try in case the backend honors it.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap

    raise ValueError(f"Unsupported CAMERA_SOURCE type: {type(source)}")


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE or event == cv2.EVENT_LBUTTONDOWN:
        mouse_state["x"] = x
        mouse_state["y"] = y


def detection_centers(corners):
    if corners is None:
        return []
    centers = []
    for marker_corners in corners:
        pts = marker_corners.reshape(4, 2)
        centers.append(tuple(np.mean(pts, axis=0)))
    return centers


def nearest_detection_index(corners, x, y, max_distance=50.0):
    centers = detection_centers(corners)
    if not centers:
        return None

    target = np.array([float(x), float(y)], dtype=np.float32)
    distances = [float(np.linalg.norm(np.array(center, dtype=np.float32) - target)) for center in centers]
    best_idx = int(np.argmin(distances))
    if distances[best_idx] > max_distance:
        return None
    return best_idx


def build_dense_world_map(homography, image_shape):
    """Return an HxWx2 float32 array mapping every pixel to world cm."""
    height, width = image_shape[:2]
    xs, ys = np.meshgrid(np.arange(width, dtype=np.float32),
                         np.arange(height, dtype=np.float32))
    pixels = np.stack([xs, ys], axis=-1).reshape(-1, 1, 2)
    world = cv2.perspectiveTransform(pixels, homography)
    return world.reshape(height, width, 2).astype(np.float32)


def build_assigned_correspondences(corners, ids, detection_to_slot, world_specs):
    """Build correspondences from explicit user-selected detection->slot assignments."""
    if ids is None or corners is None:
        return None, None

    image_pts = []
    world_pts = []
    for slot_index, detection_index in sorted(detection_to_slot.items()):
        if detection_index < 0 or detection_index >= len(corners):
            return None, None

        pts = corners[detection_index].reshape(4, 2)
        spec = world_specs[slot_index]
        image_pts.append(pts)
        world_pts.append(marker_world_corners(spec["center_cm"], spec["length_cm"]))

    if not image_pts:
        return None, None

    return (np.vstack(image_pts).astype(np.float32),
            np.vstack(world_pts).astype(np.float32))


def build_ordered_correspondences(corners, world_specs):
    """Map detections to world slots by detection order: 0 -> slot 1, 1 -> slot 2, etc."""
    if corners is None or len(corners) < len(world_specs):
        return None, None

    image_pts = []
    world_pts = []
    for slot_index, spec in enumerate(world_specs):
        pts = corners[slot_index].reshape(4, 2)
        image_pts.append(pts)
        world_pts.append(marker_world_corners(spec["center_cm"], spec["length_cm"]))

    return (np.vstack(image_pts).astype(np.float32),
            np.vstack(world_pts).astype(np.float32))


def marker_world_corners(center_xy, length_cm):
    """Corners in order: top-left, top-right, bottom-right, bottom-left,
    same convention as cv2.aruco's corner order, offset to this marker's
    real-world center."""
    cx, cy = center_xy
    h = length_cm / 2.0
    return np.array([
        [cx - h, cy + h],
        [cx + h, cy + h],
        [cx + h, cy - h],
        [cx - h, cy - h],
    ], dtype=np.float32)


def detect_markers_best(frame):
    """Try multiple dictionaries + simple preprocessing and keep the best detection."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)
    gray_up = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray_eq_up = cv2.resize(gray_eq, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # Unsharp mask often helps compressed IP streams.
    blur = cv2.GaussianBlur(gray_eq, (0, 0), 1.2)
    sharp = cv2.addWeighted(gray_eq, 1.7, blur, -0.7, 0)

    variants = [
        (gray, 1.0),
        (gray_eq, 1.0),
        (sharp, 1.0),
        (gray_up, 0.5),
        (gray_eq_up, 0.5),
    ]

    best = (None, None, None, "none", 0)  # corners, ids, rejected, dict_name, rejected_count
    best_count = -1
    best_rejected = -1

    for dict_name, detector in DETECTORS:
        for img, scale_back in variants:
            corners, ids, rejected = detector.detectMarkers(img)
            count = 0 if ids is None else len(ids)
            rejected_count = 0 if rejected is None else len(rejected)

            if corners is not None and scale_back != 1.0:
                scaled = []
                for c in corners:
                    scaled.append(c.astype(np.float32) * scale_back)
                corners = scaled

            # Prefer more decoded markers; tie-break with more rejected candidates
            # (indicates detector is at least seeing plausible quads).
            if count > best_count or (count == best_count and rejected_count > best_rejected):
                best = (corners, ids, rejected, dict_name, rejected_count)
                best_count = count
                best_rejected = rejected_count

    return best


def marker_instances_by_id():
    """Normalize MARKERS into {id: [instance_dict, ...]} for matching."""
    normalized = {}
    for marker_id, spec in MARKERS.items():
        mid = int(marker_id)
        if isinstance(spec, dict):
            normalized[mid] = [spec]
        elif isinstance(spec, (list, tuple)):
            normalized[mid] = list(spec)
        else:
            raise ValueError(f"Invalid MARKERS entry for id {marker_id}: {type(spec)}")
    return normalized


def ordered_world_specs():
    """Return the configured marker instances when there is exactly one ID group."""
    known_ids = sorted(marker_instances_by_id().keys())
    if len(known_ids) != 1:
        return None

    specs = MARKERS[known_ids[0]]
    if isinstance(specs, (list, tuple)):
        return list(specs)
    return None


def id_group_candidates(detected_markers, landmark_specs):
    """Return all possible pairing candidates for one marker ID group."""
    n_det = len(detected_markers)
    n_landmarks = len(landmark_specs)
    k = min(n_det, n_landmarks)
    if k == 0:
        return []

    candidates = []
    for det_idxs in combinations(range(n_det), k):
        for world_idxs in combinations(range(n_landmarks), k):
            for perm_world_idxs in permutations(world_idxs):
                image_blocks = [detected_markers[i].reshape(4, 2) for i in det_idxs]
                world_blocks = [
                    marker_world_corners(
                        landmark_specs[j]["center_cm"],
                        landmark_specs[j]["length_cm"],
                    )
                    for j in perm_world_idxs
                ]
                candidates.append((image_blocks, world_blocks))

    return candidates


def collect_correspondences(corners, ids):
    """
    Given one frame's detected marker corners/ids, return stacked
    (image_pts, world_pts) for detected markers that match our known
    landmarks. Supports repeated IDs by searching assignment permutations
    and selecting the fit with best inlier count and reprojection error.
    Returns (None, None) if none matched.
    """
    if ids is None:
        return None, None

    known_by_id = marker_instances_by_id()
    detections_by_id = {}
    for marker_corners, marker_id in zip(corners, ids.flatten()):
        marker_id = int(marker_id)
        detections_by_id.setdefault(marker_id, []).append(marker_corners)

    for marker_id, detected_markers in detections_by_id.items():
        if marker_id in known_by_id and len(detected_markers) > len(known_by_id[marker_id]):
            print(
                f"INFO: detected {len(detected_markers)} instance(s) of ID {marker_id} "
                f"but only {len(known_by_id[marker_id])} configured in MARKERS"
            )

    group_candidates = []
    for marker_id, detected_markers in detections_by_id.items():
        if marker_id not in known_by_id:
            continue  # unknown marker (e.g. the cart's marker) -- skip

        candidates = id_group_candidates(detected_markers, known_by_id[marker_id])
        if candidates:
            group_candidates.append(candidates)

    if not group_candidates:
        return None, None

    best_score = None
    best_pair = None

    for combo in product(*group_candidates):
        image_blocks = []
        world_blocks = []
        for img_group, world_group in combo:
            image_blocks.extend(img_group)
            world_blocks.extend(world_group)

        image_pts = np.vstack(image_blocks).astype(np.float32)
        world_pts = np.vstack(world_blocks).astype(np.float32)
        if len(image_pts) < 4:
            continue

        H, status = cv2.findHomography(image_pts, world_pts, method=cv2.RANSAC)
        if H is None:
            continue

        reproj = cv2.perspectiveTransform(image_pts.reshape(-1, 1, 2), H).reshape(-1, 2)
        errors = np.linalg.norm(reproj - world_pts, axis=1)

        if status is not None:
            inliers = status.ravel().astype(bool)
            inlier_count = int(np.sum(inliers))
            if inlier_count > 0:
                mean_error = float(np.mean(errors[inliers]))
            else:
                mean_error = float(np.mean(errors))
        else:
            inlier_count = len(image_pts)
            mean_error = float(np.mean(errors))

        score = (-inlier_count, mean_error)
        if best_score is None or score < best_score:
            best_score = score
            best_pair = (image_pts, world_pts)

    if best_pair is None:
        return None, None

    return best_pair


def save_homography(homography, camera_name, markers_used):
    """Persist the fitted homography and the metadata needed to reload it."""
    if homography is None:
        raise ValueError("Cannot save a homography before one has been computed.")

    out_path = f"H_{camera_name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"H": homography.tolist(), "camera": camera_name,
                   "markers_used": markers_used}, f, indent=2)
    return out_path


def main():
    global H_CURRENT, FRAME_SHAPE
    global selected_detection_idx, slot_to_detection_idx

    cap = open_camera(CAMERA_SOURCE)
    if not cap.isOpened():
        print(f"ERROR: could not open camera source {CAMERA_SOURCE}")
        sys.exit(1)

    cv2.namedWindow("Multi-marker calibration", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Multi-marker calibration", on_mouse)
    cv2.moveWindow("Multi-marker calibration", 50, 50)
    cv2.resizeWindow("Multi-marker calibration", 900, 650)

    history = []
    known_ids = sorted(marker_instances_by_id().keys())
    world_specs = ordered_world_specs()

    print(f"Looking for markers with IDs {known_ids}.")
    if world_specs is not None:
        print("Using detection order: detection #0 -> slot 1, #1 -> slot 2, #2 -> slot 3.")
    print("Press 'q' to quit early.")

    if MANUAL_ASSIGNMENT_MODE and world_specs is None:
        print("NOTE: manual marker assignment is designed for one same-ID group with multiple physical markers.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Frame grab failed.")
            break

        FRAME_SHAPE = frame.shape

        corners, ids, _, active_dict, rejected_count = detect_markers_best(frame)
        display = frame.copy()
        if ids is not None and corners is not None:
            cv2.aruco.drawDetectedMarkers(display, corners, ids)

        detected_ids = [] if ids is None else [int(x) for x in ids.flatten()]

        centers = detection_centers(corners)

        if world_specs is not None:
            for idx, center in enumerate(centers):
                color = (0, 255, 0)
                cv2.circle(display, (int(center[0]), int(center[1])), 8, color, 2)
                cv2.putText(display, f"#{idx}", (int(center[0]) + 8, int(center[1]) - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        if world_specs is not None and corners is not None and len(corners) >= len(world_specs):
            image_pts, world_pts = build_ordered_correspondences(corners, world_specs)
        else:
            image_pts, world_pts = collect_correspondences(corners, ids)

        if image_pts is None:
            history.clear()
            if detected_ids:
                msg = f"Detected IDs {detected_ids}, check MARKERS config"
            else:
                msg = "No marker detected"
            cv2.putText(display, msg,
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
        else:
            n_markers = len(image_pts) // 4
            history.append((image_pts, world_pts))
            cv2.putText(display, f"Seeing {n_markers} landmark marker(s) - "
                                  f"stable frames: {len(history)}/{STABILITY_FRAMES}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(display, f"Dict: {active_dict} | Raw IDs: {detected_ids} | Rejected: {rejected_count}",
                    (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

        if image_pts is not None and len(history) >= STABILITY_FRAMES and H_CURRENT is None:
            # use the most recent stable frame's correspondences
            image_pts_final, world_pts_final = history[-1]
            H, status = cv2.findHomography(image_pts_final, world_pts_final,
                                            method=cv2.RANSAC)
            if H is None:
                print("Could not fit a homography from the current stable frame.")
                history.clear()
                continue

            H_CURRENT = H
            out_path = save_homography(H, CAMERA_NAME, known_ids)
            print(f"\nLOCKED IN. Saved homography to {out_path}")
            print(H)
            if EXPORT_DENSE_WORLD_MAP and FRAME_SHAPE is not None:
                dense_world_map = build_dense_world_map(H_CURRENT, FRAME_SHAPE)
                map_path = f"world_map_{CAMERA_NAME}.npy"
                meta_path = f"world_map_{CAMERA_NAME}_meta.json"
                np.save(map_path, dense_world_map)
                with open(meta_path, "w") as f:
                    json.dump({
                        "camera": CAMERA_NAME,
                        "shape": list(dense_world_map.shape),
                        "dtype": str(dense_world_map.dtype),
                        "meaning": "world_map[y, x] -> [world_x_cm, world_y_cm]",
                        "source": "multi_marker_homography.py",
                    }, f, indent=2)
                print(f"Saved dense world map to {map_path}")
                print(f"Saved metadata to {meta_path}")
            print("\nCalibration done -- move the mouse over the window to see pixel/world coordinates.")

        if H_CURRENT is not None and mouse_state["x"] is not None and mouse_state["y"] is not None:
            px = np.array([[[float(mouse_state["x"]), float(mouse_state["y"])]]], dtype=np.float32)
            world = cv2.perspectiveTransform(px, H_CURRENT)[0][0]
            coord_msg = f"Mouse px=({mouse_state['x']}, {mouse_state['y']}) -> world=({world[0]:.1f}, {world[1]:.1f}) cm"
            cv2.putText(display, coord_msg,
                        (10, 86), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
            if len(history) >= STABILITY_FRAMES:
                cv2.putText(display, "H saved: mouse movement now reports world coordinates",
                            (10, 112), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

        cv2.imshow("Multi-marker calibration", display)
        key = cv2.waitKey(1) & 0xFF

        if MANUAL_ASSIGNMENT_MODE and world_specs is not None:
            if key in (ord('1'), ord('2'), ord('3')):
                if selected_detection_idx is not None:
                    slot_index = int(chr(key)) - 1
                    if slot_index < len(world_specs):
                        slot_to_detection_idx[slot_index] = selected_detection_idx
                        print(f"Assigned slot {slot_index + 1} -> detection #{selected_detection_idx}")
                else:
                    print("No marker selected. Click a marker first, then press 1/2/3.")
            elif key == ord('c'):
                selected_detection_idx = None
                slot_to_detection_idx.clear()
                H_CURRENT = None
                print("Cleared manual assignments.")
            elif key == ord('q'):
                break
        else:
            if key == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
