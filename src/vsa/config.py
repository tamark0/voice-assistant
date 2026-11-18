import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "signs.db"
SIGNS_DIR = ROOT / "assets" / "signs"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama_chat/qwen3:8b")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
APP_NAME = "voice_sign_assistant"