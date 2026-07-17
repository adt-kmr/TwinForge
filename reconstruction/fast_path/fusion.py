import open3d as o3d


def tsdf_fusion(rgbd_images, volume_size: float = 4.0):
    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=volume_size / 512.0,
        sdf_trunc=0.04,
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8,
    )
    return volume
