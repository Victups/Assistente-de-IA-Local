from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    id: str = Field(..., description="Identificador da conversa")
    title: str = Field(..., description="Título da conversa")
    updated_at: str = Field(..., description="Data da última atualização")


class MessageDto(BaseModel):
    id: str = Field(..., description="Identificador da mensagem")
    role: str = Field(..., description="Papel: user ou assistant")
    content: str = Field(..., description="Conteúdo da mensagem")
    transcription_source: str | None = Field(
        default=None,
        description="Origem da transcrição: voice ou video",
    )
    is_system: bool = Field(default=False, description="Mensagem de sistema")
    created_at: str = Field(..., description="Data de criação")


class ConversationDetail(BaseModel):
    id: str = Field(..., description="Identificador da conversa")
    title: str = Field(..., description="Título da conversa")
    document_id: str | None = Field(default=None, description="Documento anexado")
    doc_type: str | None = Field(default=None, description="Tipo do documento anexado")
    attachment_filename: str | None = Field(default=None, description="Nome do arquivo anexado")
    messages: list[MessageDto] = Field(default_factory=list)
    created_at: str = Field(..., description="Data de criação")
    updated_at: str = Field(..., description="Data da última atualização")


class CreateConversationRequest(BaseModel):
    title: str = Field(default="Nova conversa", min_length=1, max_length=120)


class UpdateConversationRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    document_id: str | None = None
    doc_type: str | None = None
    attachment_filename: str | None = None


class CreateMessageRequest(BaseModel):
    role: str = Field(..., description="Papel: user ou assistant")
    content: str = Field(..., min_length=1, description="Conteúdo da mensagem")
    transcription_source: str | None = None
    is_system: bool = False
