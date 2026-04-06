"""
IMOBILAY — SessionRepository

CRUD para a tabela sessions (conversas do usuário).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class SessionRecord:
    id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime
    last_active: datetime


class SessionRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def create(self, user_id: str, title: str | None = None) -> SessionRecord:
        result = await (
            self._db.table("sessions")
            .insert({"user_id": user_id, "title": title})
            .execute()
        )
        return self._map(result.data[0])

    async def get_by_id(self, session_id: str) -> SessionRecord | None:
        result = await (
            self._db.table("sessions")
            .select("*")
            .eq("id", session_id)
            .limit(1)
            .execute()
        )
        return self._map(result.data[0]) if result.data else None

    async def list_by_user(self, user_id: str, limit: int = 50) -> list[SessionRecord]:
        result = await (
            self._db.table("sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("last_active", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    async def update_last_active(self, session_id: str) -> None:
        await (
            self._db.table("sessions")
            .update({"last_active": datetime.utcnow().isoformat()})
            .eq("id", session_id)
            .execute()
        )

    async def update_title(self, session_id: str, title: str) -> None:
        await (
            self._db.table("sessions")
            .update({"title": title})
            .eq("id", session_id)
            .execute()
        )

    async def delete(self, session_id: str) -> None:
        await (
            self._db.table("sessions")
            .delete()
            .eq("id", session_id)
            .execute()
        )

    def _map(self, row: dict) -> SessionRecord:
        return SessionRecord(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            title=row.get("title"),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_active=datetime.fromisoformat(row["last_active"]),
        )
