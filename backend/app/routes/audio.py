from fastapi import APIRouter, File, UploadFile

from app.models.document import DocumentChatRequest, DocumentChatResponse, DocumentUploadResponse
from app.services.audio_service import AudioService
from app.services.ollama_service import OllamaService
from app.services.upload_response import build_upload_response

router = APIRouter(prefix="/api/audio", tags=["Áudio"])
audio_service = AudioService()
ollama_service = OllamaService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_audio(file: UploadFile = File(...)) -> DocumentUploadResponse:
    document = await audio_service.upload(file)
    return build_upload_response(document)


@router.post("/chat", response_model=DocumentChatResponse)
async def chat_with_audio(request: DocumentChatRequest) -> DocumentChatResponse:
    document = audio_service.get_document(request.document_id)
    response_text = await ollama_service.generate_with_context(
        message=request.message,
        context=document.content,
        source_label="áudio transcrito",
    )
    return DocumentChatResponse(response=response_text)
