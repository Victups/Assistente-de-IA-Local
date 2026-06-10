import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

from app.config import UPLOAD_DIR


@dataclass
class StoredDocument:
    document_id: str
    filename: str
    doc_type: str
    content: str
    created_at: str


class DocumentStore:
    def __init__(self) -> None:
        self.storage_dir = UPLOAD_DIR
        self.metadata_dir = self.storage_dir / "metadata"
        self.files_dir = self.storage_dir / "files"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        filename: str,
        doc_type: str,
        content: str,
        file_bytes: bytes,
    ) -> StoredDocument:
        document_id = str(uuid.uuid4())
        extension = Path(filename).suffix.lower()
        stored_filename = f"{document_id}{extension}"
        file_path = self.files_dir / stored_filename
        file_path.write_bytes(file_bytes)

        document = StoredDocument(
            document_id=document_id,
            filename=filename,
            doc_type=doc_type,
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        metadata_path = self.metadata_dir / f"{document_id}.json"
        metadata_path.write_text(
            json.dumps(asdict(document), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return document

    def get(self, document_id: str) -> StoredDocument:
        metadata_path = self.metadata_dir / f"{document_id}.json"

        if not metadata_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Documento não encontrado, identificador {document_id}",
            )

        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        return StoredDocument(**data)

    def update_content(self, document_id: str, content: str) -> StoredDocument:
        document = self.get(document_id)
        updated = StoredDocument(
            document_id=document.document_id,
            filename=document.filename,
            doc_type=document.doc_type,
            content=content,
            created_at=document.created_at,
        )

        metadata_path = self.metadata_dir / f"{document_id}.json"
        metadata_path.write_text(
            json.dumps(asdict(updated), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return updated
