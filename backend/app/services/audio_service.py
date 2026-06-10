from fastapi import HTTPException, UploadFile

from app.config import ALLOWED_AUDIO_EXTENSIONS, MAX_UPLOAD_SIZE_MB, UPLOAD_DIR
from app.services.document_store import DocumentStore, StoredDocument
from app.services.whisper_service import WhisperService


class AudioService:
    def __init__(self) -> None:
        self.document_store = DocumentStore()
        self.whisper_service = WhisperService()
        self.max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    async def upload(self, file: UploadFile) -> StoredDocument:
        filename = file.filename or "audio.wav"
        extension = self._validate_extension(filename)
        file_bytes = await self._read_file(file)

        document = self.document_store.create(
            filename=filename,
            doc_type="audio",
            content="",
            file_bytes=file_bytes,
        )

        audio_path = UPLOAD_DIR / "files" / f"{document.document_id}{extension}"
        transcription = await self.whisper_service.transcribe(audio_path)

        return self.document_store.update_content(document.document_id, transcription)

    def get_document(self, document_id: str) -> StoredDocument:
        document = self.document_store.get(document_id)

        if document.doc_type != "audio":
            raise HTTPException(
                status_code=400,
                detail="Não é possível utilizar este identificador para chat com áudio.",
            )

        return document

    def _validate_extension(self, filename: str) -> str:
        extension = f".{filename.rsplit('.', 1)[-1].lower()}" if "." in filename else ""

        if extension not in ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Não é possível processar o arquivo. Envie um áudio válido (mp3, wav, m4a, ogg, webm, flac).",
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
