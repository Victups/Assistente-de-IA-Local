from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Identificador do documento processado")
    filename: str = Field(..., description="Nome original do arquivo")
    doc_type: str = Field(..., description="Tipo do documento")
    preview: str = Field(..., description="Prévia do conteúdo extraído")
    transcription: str = Field(..., description="Texto completo transcrito ou extraído")
    content_length: int = Field(..., description="Tamanho total do conteúdo em caracteres")


class DocumentChatRequest(BaseModel):
    document_id: str = Field(..., min_length=1, description="Identificador do documento")
    message: str = Field(..., min_length=1, description="Mensagem do usuário")


class DocumentChatResponse(BaseModel):
    response: str = Field(..., description="Resposta gerada pela IA")
