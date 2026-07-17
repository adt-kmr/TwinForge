def run_colmap_pipeline(image_dir: str, output_dir: str):
    return {"status": "colmap_dense", "output": output_dir}


def run_nerfstudio(transforms_path: str):
    return {"status": "nerf_training", "config": transforms_path}
