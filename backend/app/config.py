import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
CHAT_DB_PATH = Path(os.getenv("CHAT_DB_PATH", DATA_DIR / "chat.db"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".flac"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".avi", ".mov", ".mkv"}
