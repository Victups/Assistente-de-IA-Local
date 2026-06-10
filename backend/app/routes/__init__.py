from app.routes.audio import router as audio_router
from app.routes.chat import router as chat_router
from app.routes.pdf import router as pdf_router
from app.routes.video import router as video_router

__all__ = ["audio_router", "chat_router", "pdf_router", "video_router"]
