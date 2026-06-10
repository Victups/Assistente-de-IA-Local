import asyncio
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException
from faster_whisper import WhisperModel

from app.config import WHISPER_MODEL


class WhisperService:
    @staticmethod
    @lru_cache(maxsize=1)
    def _get_model() -> WhisperModel:
        return WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

    async def transcribe(self, audio_path: Path) -> str:
        loop = asyncio.get_running_loop()

        try:
            text = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_path,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Não foi possível transcrever o áudio.",
            ) from exc

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Não foi possível identificar fala no áudio enviado.",
            )

        return text

    def _transcribe_sync(self, audio_path: Path) -> str:
        model = self._get_model()
        segments, _info = model.transcribe(str(audio_path), beam_size=5)
        return " ".join(segment.text.strip() for segment in segments if segment.text.strip())
