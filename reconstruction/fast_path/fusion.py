"""Fast-path reconstruction: depth-frame fusion into a voxel-deduped point cloud.

Frames are dicts with keys: depth (H,W float32 metres), intrinsics (3,3),
pose (4,4 camera->world), optional color (H,W,3 uint8).
Uses Open3D TSDF when available; the numpy path is the always-works fallback.
"""
import numpy as np


def backproject(frame: dict) -> tuple:
    """One RGB-D frame -> (Nx3 world points, Nx3 uint8 colors)."""
    depth = np.asarray(frame["depth"], dtype=np.float64)
    K = np.asarray(frame["intrinsics"], dtype=np.float64)
    pose = np.asarray(frame["pose"], dtype=np.float64)
    h, w = depth.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    valid = depth > 0
    z = depth[valid]
    x = (u[valid] - K[0, 2]) * z / K[0, 0]
    y = (v[valid] - K[1, 2]) * z / K[1, 1]
    pts_cam = np.stack([x, y, z, np.ones_like(z)], axis=1)
    pts = (pose @ pts_cam.T).T[:, :3]
    if frame.get("color") is not None:
        colors = np.asarray(frame["color"])[valid]
    else:
        colors = np.full((len(pts), 3), 200, dtype=np.uint8)
    return pts, colors


def voxel_dedup(points, colors, voxel_size: float):
    """Keep one point (first seen) per voxel cell."""
    keys = np.floor(points / voxel_size).astype(np.int64)
    _, idx = np.unique(keys, axis=0, return_index=True)
    idx.sort()
    return points[idx], colors[idx]


def fuse_frames(frames, voxel_size: float = 0.02) -> tuple:
    """Fuse RGB-D frames into a voxel-deduped point cloud."""
    all_pts, all_cols = [], []
    for f in frames:
        p, c = backproject(f)
        all_pts.append(p)
        all_cols.append(c)
    points = np.concatenate(all_pts)
    colors = np.concatenate(all_cols)
    return voxel_dedup(points, colors, voxel_size)


def tsdf_fusion(frames, voxel_size: float = 0.02):
    """Open3D ScalableTSDFVolume backend; raises ImportError without open3d."""
    import open3d as o3d

    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=voxel_size,
        sdf_trunc=voxel_size * 4,
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8,
    )
    for f in frames:
        depth = np.asarray(f["depth"], dtype=np.float32)
        color = np.asarray(
            f.get("color") if f.get("color") is not None
            else np.full((*depth.shape, 3), 200, dtype=np.uint8)
        )
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            o3d.geometry.Image(np.ascontiguousarray(color)),
            o3d.geometry.Image(depth),
            depth_scale=1.0, depth_trunc=10.0, convert_rgb_to_intensity=False,
        )
        K = np.asarray(f["intrinsics"])
        h, w = depth.shape
        intrinsic = o3d.camera.PinholeCameraIntrinsic(
            w, h, K[0, 0], K[1, 1], K[0, 2], K[1, 2]
        )
        volume.integrate(rgbd, intrinsic, np.linalg.inv(np.asarray(f["pose"])))
    return volume
