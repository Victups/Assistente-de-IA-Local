from fastapi import APIRouter

from app.models.conversation import (
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
    CreateMessageRequest,
    MessageDto,
    UpdateConversationRequest,
)
from app.services.chat_history_service import ChatHistoryService

router = APIRouter(prefix="/api/conversations", tags=["Conversas"])
chat_history_service = ChatHistoryService()


@router.get("", response_model=list[ConversationSummary])
async def list_conversations() -> list[ConversationSummary]:
    return chat_history_service.list_conversations()


@router.post("", response_model=ConversationSummary)
async def create_conversation(
    request: CreateConversationRequest,
) -> ConversationSummary:
    return chat_history_service.create_conversation(request)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str) -> ConversationDetail:
    return chat_history_service.get_conversation(conversation_id)


@router.patch("/{conversation_id}", response_model=ConversationSummary)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
) -> ConversationSummary:
    return chat_history_service.update_conversation(conversation_id, request)


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict[str, str]:
    chat_history_service.delete_conversation(conversation_id)
    return {"status": "deleted"}


@router.post("/{conversation_id}/messages", response_model=MessageDto)
async def add_message(
    conversation_id: str,
    request: CreateMessageRequest,
) -> MessageDto:
    return chat_history_service.add_message(conversation_id, request)


@router.get("/{conversation_id}/attachment")
async def get_conversation_attachment(conversation_id: str) -> dict | None:
    return chat_history_service.get_attachment_context(conversation_id)
