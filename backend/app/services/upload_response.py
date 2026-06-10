from app.models.document import DocumentUploadResponse
from app.services.document_store import StoredDocument


def build_upload_response(document: StoredDocument) -> DocumentUploadResponse:
    preview_limit = 500
    preview = document.content[:preview_limit]
    if len(document.content) > preview_limit:
        preview = f"{preview}..."

    return DocumentUploadResponse(
        document_id=document.document_id,
        filename=document.filename,
        doc_type=document.doc_type,
        preview=preview,
        content_length=len(document.content),
    )
