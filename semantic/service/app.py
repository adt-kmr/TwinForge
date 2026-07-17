from fastapi import FastAPI

from .inference import segment_image

app = FastAPI(title="Semantic Service")


@app.post("/segment")
async def segment(image_path: str):
    return segment_image(image_path)
