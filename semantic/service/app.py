from fastapi import FastAPI, HTTPException

from reconstruction.reconstruct import read_ply

from .inference import segment_image, segment_points

app = FastAPI(title="Semantic Service")


@app.post("/segment")
async def segment(body: dict):
    """Accepts {"ply_path": ...} for 3D clouds or {"image_path": ...} for frames."""
    if ply_path := body.get("ply_path"):
        points, colors = read_ply(ply_path)
        return {"objects": segment_points(points, colors)}
    if image_path := body.get("image_path"):
        return segment_image(image_path)
    raise HTTPException(400, "provide ply_path or image_path")
