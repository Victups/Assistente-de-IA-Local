from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.ollama_service import OllamaService

router = APIRouter(prefix="/api", tags=["Chat"])
ollama_service = OllamaService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    response_text = await ollama_service.generate_response(request.message)
    return ChatResponse(response=response_text)
