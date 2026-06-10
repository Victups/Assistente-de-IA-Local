import sqlite3
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import CHAT_DB_PATH, DATA_DIR
from app.models.conversation import (
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
    CreateMessageRequest,
    MessageDto,
    UpdateConversationRequest,
)
from app.services.document_store import DocumentStore


class ChatHistoryService:
    def __init__(self) -> None:
        self.db_path = CHAT_DB_PATH
        self.document_store = DocumentStore()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    document_id TEXT,
                    doc_type TEXT,
                    attachment_filename TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    transcription_source TEXT,
                    is_system INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, created_at);
                """
            )

    def list_conversations(self) -> list[ConversationSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [
            ConversationSummary(
                id=row["id"],
                title=row["title"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def create_conversation(
        self,
        request: CreateConversationRequest,
    ) -> ConversationSummary:
        conversation_id = str(uuid.uuid4())
        now = self._now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations (
                    id, title, created_at, updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (conversation_id, request.title, now, now),
            )

        return ConversationSummary(
            id=conversation_id,
            title=request.title,
            updated_at=now,
        )

    def get_conversation(self, conversation_id: str) -> ConversationDetail:
        conversation = self._get_conversation_row(conversation_id)

        with self._connect() as connection:
            message_rows = connection.execute(
                """
                SELECT id, role, content, transcription_source, is_system, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            ).fetchall()

        return ConversationDetail(
            id=conversation["id"],
            title=conversation["title"],
            document_id=conversation["document_id"],
            doc_type=conversation["doc_type"],
            attachment_filename=conversation["attachment_filename"],
            messages=[
                MessageDto(
                    id=row["id"],
                    role=row["role"],
                    content=row["content"],
                    transcription_source=row["transcription_source"],
                    is_system=bool(row["is_system"]),
                    created_at=row["created_at"],
                )
                for row in message_rows
            ],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
        )

    def update_conversation(
        self,
        conversation_id: str,
        request: UpdateConversationRequest,
    ) -> ConversationSummary:
        self._get_conversation_row(conversation_id)
        fields = []
        values: list[str | None] = []
        fields_set = request.model_fields_set

        if "title" in fields_set and request.title is not None:
            fields.append("title = ?")
            values.append(request.title)

        if "document_id" in fields_set:
            fields.append("document_id = ?")
            values.append(request.document_id)

        if "doc_type" in fields_set:
            fields.append("doc_type = ?")
            values.append(request.doc_type)

        if "attachment_filename" in fields_set:
            fields.append("attachment_filename = ?")
            values.append(request.attachment_filename)

        if not fields:
            conversation = self._get_conversation_row(conversation_id)
            return ConversationSummary(
                id=conversation["id"],
                title=conversation["title"],
                updated_at=conversation["updated_at"],
            )

        now = self._now()
        fields.append("updated_at = ?")
        values.append(now)
        values.append(conversation_id)

        with self._connect() as connection:
            connection.execute(
                f"UPDATE conversations SET {', '.join(fields)} WHERE id = ?",
                values,
            )

        conversation = self._get_conversation_row(conversation_id)
        return ConversationSummary(
            id=conversation["id"],
            title=conversation["title"],
            updated_at=conversation["updated_at"],
        )

    def delete_conversation(self, conversation_id: str) -> None:
        self._get_conversation_row(conversation_id)

        with self._connect() as connection:
            connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id,),
            )
            connection.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,),
            )

    def add_message(
        self,
        conversation_id: str,
        request: CreateMessageRequest,
    ) -> MessageDto:
        conversation = self._get_conversation_row(conversation_id)
        message_id = str(uuid.uuid4())
        now = self._now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    id, conversation_id, role, content,
                    transcription_source, is_system, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    request.role,
                    request.content,
                    request.transcription_source,
                    int(request.is_system),
                    now,
                ),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )

        if request.role == "user" and conversation["title"] == "Nova conversa":
            self.update_conversation(
                conversation_id,
                UpdateConversationRequest(title=self._build_title(request.content)),
            )

        return MessageDto(
            id=message_id,
            role=request.role,
            content=request.content,
            transcription_source=request.transcription_source,
            is_system=request.is_system,
            created_at=now,
        )

    def get_attachment_context(self, conversation_id: str) -> dict[str, str] | None:
        conversation = self._get_conversation_row(conversation_id)

        if not conversation["document_id"] or not conversation["doc_type"]:
            return None

        try:
            document = self.document_store.get(conversation["document_id"])
        except HTTPException:
            return None

        return {
            "document_id": document.document_id,
            "doc_type": document.doc_type,
            "filename": conversation["attachment_filename"] or document.filename,
            "transcription": document.content,
            "preview": document.content[:500],
            "content_length": str(len(document.content)),
        }

    def _get_conversation_row(self, conversation_id: str) -> sqlite3.Row:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, title, document_id, doc_type, attachment_filename,
                       created_at, updated_at
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Conversa não encontrada, identificador {conversation_id}",
            )

        return row

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _build_title(content: str) -> str:
        normalized = " ".join(content.split())
        if len(normalized) <= 48:
            return normalized or "Nova conversa"
        return f"{normalized[:48].rstrip()}..."
