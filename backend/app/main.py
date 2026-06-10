from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATA_DIR, UPLOAD_DIR
from app.routes.audio import router as audio_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router
from app.routes.pdf import router as pdf_router
from app.routes.video import router as video_router

app = FastAPI(
    title="Assistente de IA Local",
    description="API de chat local utilizando Ollama, Phi-3, PDF, áudio e vídeo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(pdf_router)
app.include_router(audio_router)
app.include_router(video_router)


@app.on_event("startup")
async def startup() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "files").mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "metadata").mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health() -> dict[str, str | list[str]]:
    return {
        "status": "ok",
        "features": ["chat", "pdf", "audio", "video", "history"],
    }
