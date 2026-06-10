import asyncio
import subprocess
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import ALLOWED_VIDEO_EXTENSIONS, FFMPEG_PATH, MAX_UPLOAD_SIZE_MB, UPLOAD_DIR
from app.services.document_store import DocumentStore, StoredDocument
from app.services.whisper_service import WhisperService


class VideoService:
    def __init__(self) -> None:
        self.document_store = DocumentStore()
        self.whisper_service = WhisperService()
        self.max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    async def upload(self, file: UploadFile) -> StoredDocument:
        filename = file.filename or "video.mp4"
        extension = self._validate_extension(filename)
        file_bytes = await self._read_file(file)

        document = self.document_store.create(
            filename=filename,
            doc_type="video",
            content="",
            file_bytes=file_bytes,
        )

        video_path = UPLOAD_DIR / "files" / f"{document.document_id}{extension}"
        audio_path = UPLOAD_DIR / "files" / f"{document.document_id}_audio.wav"

        await self._extract_audio(video_path, audio_path)
        transcription = await self.whisper_service.transcribe(audio_path)

        audio_path.unlink(missing_ok=True)

        return self.document_store.update_content(document.document_id, transcription)

    def get_document(self, document_id: str) -> StoredDocument:
        document = self.document_store.get(document_id)

        if document.doc_type != "video":
            raise HTTPException(
                status_code=400,
                detail="Não é possível utilizar este identificador para chat com vídeo.",
            )

        return document

    async def _extract_audio(self, video_path: Path, audio_path: Path) -> None:
        loop = asyncio.get_running_loop()

        try:
            await loop.run_in_executor(
                None,
                self._extract_audio_sync,
                video_path,
                audio_path,
            )
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=503,
                detail="FFmpeg não encontrado. Instale o FFmpeg e adicione-o ao PATH do sistema.",
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="ignore") if exc.stderr else str(exc)
            raise HTTPException(
                status_code=400,
                detail=f"Não foi possível extrair áudio do vídeo: {stderr}",
            ) from exc

    def _extract_audio_sync(self, video_path: Path, audio_path: Path) -> None:
        command = [
            FFMPEG_PATH,
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(audio_path),
            "-y",
        ]

        subprocess.run(
            command,
            check=True,
            capture_output=True,
        )

    def _validate_extension(self, filename: str) -> str:
        extension = f".{filename.rsplit('.', 1)[-1].lower()}" if "." in filename else ""

        if extension not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Não é possível processar o arquivo. Envie um vídeo válido (mp4, webm, avi, mov, mkv).",
            )

        return extension

    async def _read_file(self, file: UploadFile) -> bytes:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="Não é possível processar um arquivo vazio.",
            )

        if len(file_bytes) > self.max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível enviar arquivos maiores que {MAX_UPLOAD_SIZE_MB}MB.",
            )

        return file_bytes
