def reconstruct(base_url: str, session_id: str, method: str = "fast") -> str:
    return f"{base_url}/reconstruct/{session_id}?method={method}"
