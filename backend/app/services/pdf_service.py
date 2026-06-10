from io import BytesIO

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from app.config import ALLOWED_PDF_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from app.services.document_store import DocumentStore, StoredDocument


class PdfService:
    def __init__(self) -> None:
        self.document_store = DocumentStore()
        self.max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    async def upload(self, file: UploadFile) -> StoredDocument:
        filename = file.filename or "documento.pdf"
        extension = self._validate_extension(filename)
        file_bytes = await self._read_file(file, extension)
        content = self._extract_text(file_bytes)

        if not content.strip():
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair texto do PDF enviado.",
            )

        return self.document_store.create(
            filename=filename,
            doc_type="pdf",
            content=content,
            file_bytes=file_bytes,
        )

    def get_document(self, document_id: str) -> StoredDocument:
        document = self.document_store.get(document_id)

        if document.doc_type != "pdf":
            raise HTTPException(
                status_code=400,
                detail="Não é possível utilizar este identificador para chat com PDF.",
            )

        return document

    def _validate_extension(self, filename: str) -> str:
        extension = f".{filename.rsplit('.', 1)[-1].lower()}" if "." in filename else ""

        if extension not in ALLOWED_PDF_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Não é possível processar o arquivo. Envie um PDF válido.",
            )

        return extension

    async def _read_file(self, file: UploadFile, extension: str) -> bytes:
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

    def _extract_text(self, file_bytes: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_bytes))
            pages_text = []

            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages_text.append(page_text.strip())

            return "\n\n".join(text for text in pages_text if text)
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível ler o conteúdo do PDF.",
            ) from exc
