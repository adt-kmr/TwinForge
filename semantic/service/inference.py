LABEL_ONTOLOGY = [
    "wall", "floor", "ceiling", "door", "window",
    "chair", "table", "shelf", "cabinet",
    "robot", "person", "obstacle",
]


def segment_image(image_path: str):
    return {"labels": [], "masks": []}
