from fastapi import APIRouter, File, UploadFile

from app.models.document import DocumentChatRequest, DocumentChatResponse, DocumentUploadResponse
from app.services.ollama_service import OllamaService
from app.services.upload_response import build_upload_response
from app.services.video_service import VideoService

router = APIRouter(prefix="/api/video", tags=["Vídeo"])
video_service = VideoService()
ollama_service = OllamaService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_video(file: UploadFile = File(...)) -> DocumentUploadResponse:
    document = await video_service.upload(file)
    return build_upload_response(document)


@router.post("/chat", response_model=DocumentChatResponse)
async def chat_with_video(request: DocumentChatRequest) -> DocumentChatResponse:
    document = video_service.get_document(request.document_id)
    response_text = await ollama_service.generate_with_context(
        message=request.message,
        context=document.content,
        source_label="vídeo transcrito",
    )
    return DocumentChatResponse(response=response_text)
