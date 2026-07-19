"""Offline speech-to-text fallback: Whisper (openai-whisper), lazy-imported.

This is the only transcription backend for POST /transcribe (orchestrator/service.py) --
it is deliberately independent of SARVAM_API_KEY, which only gates the downstream
text -> task-graph step handled by sarvam.task_engine.provider.get_planner (used by the
existing /plan endpoint). There is no real Sarvam audio/speech-to-text API wired up
anywhere in this repo, so this module owns audio -> text on its own.

`openai-whisper` is not a requirements.txt dependency (same reasoning as
policy/rl/bridge.py's onnxruntime and capture/aruco.py's cv2: heavy, optional, and
genuinely absent from this dev environment) -- lazy-imported here so the rest of the
suite stays green without it installed, and this module's own absence-path is a real,
verifiable RuntimeError rather than a mock.
"""


def transcribe(audio_path: str) -> str:
    """Transcribe `audio_path` to text using Whisper's "base" model.

    Raises:
        RuntimeError: if the `whisper` (openai-whisper) package is not installed.
    """
    try:
        import whisper
    except ImportError:
        raise RuntimeError("no offline transcription backend available")

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]
