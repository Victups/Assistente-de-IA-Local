from fastapi import APIRouter, File, UploadFile

from app.models.document import DocumentChatRequest, DocumentChatResponse, DocumentUploadResponse
from app.services.ollama_service import OllamaService
from app.services.pdf_service import PdfService
from app.services.upload_response import build_upload_response

router = APIRouter(prefix="/api/pdf", tags=["PDF"])
pdf_service = PdfService()
ollama_service = OllamaService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> DocumentUploadResponse:
    document = await pdf_service.upload(file)
    return build_upload_response(document)


@router.post("/chat", response_model=DocumentChatResponse)
async def chat_with_pdf(request: DocumentChatRequest) -> DocumentChatResponse:
    document = pdf_service.get_document(request.document_id)
    response_text = await ollama_service.generate_with_context(
        message=request.message,
        context=document.content,
        source_label="documento PDF",
    )
    return DocumentChatResponse(response=response_text)
