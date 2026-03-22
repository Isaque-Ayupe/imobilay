"""
IMOBILAY — MessageRepository

CRUD para a tabela messages (turnos de conversa).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class MessageRecord:
    id: UUID
    session_id: UUID
    role: str               # "user" | "assistant"
    content: str
    trace_id: UUID | None
    created_at: datetime


class MessageRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def create(
        self,
        session_id: str,
        role: str,
        content: str,
        trace_id: str | None = None,
    ) -> MessageRecord:
        result = await (
            self._db.table("messages")
            .insert({
                "session_id": session_id,
                "role": role,
                "content": content,
                "trace_id": trace_id,
            })
            .execute()
        )
        return self._map(result.data[0])

    async def list_by_session(
        self, session_id: str, limit: int = 100
    ) -> list[MessageRecord]:
        result = await (
            self._db.table("messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    async def get_last_message(self, session_id: str) -> MessageRecord | None:
        result = await (
            self._db.table("messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        return self._map(result.data) if result.data else None

    async def count_by_session(self, session_id: str) -> int:
        result = await (
            self._db.table("messages")
            .select("*", count="exact")
            .eq("session_id", session_id)
            .limit(0)
            .execute()
        )
        return result.count or 0

    def _map(self, row: dict) -> MessageRecord:
        return MessageRecord(
            id=UUID(row["id"]),
            session_id=UUID(row["session_id"]),
            role=row["role"],
            content=row["content"],
            trace_id=UUID(row["trace_id"]) if row.get("trace_id") else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
