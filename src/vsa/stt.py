from faster_whisper import WhisperModel
from .config import WHISPER_MODEL

_model = None

def transcribe(audio_path: str) -> str:
    global _model
    if _model is None:  # load once, lazily
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _ = _model.transcribe(audio_path, language="en", vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()