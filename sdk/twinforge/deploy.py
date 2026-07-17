def deploy(base_url: str, model_id: str, target: str) -> str:
    return f"{base_url}/deploy/{model_id}/{target}"
