"""
IMOBILAY — SavedPropertyRepository

Persistência de saved_properties (snapshots imutáveis de imóveis).
Regra R7: property_data é JSONB imutável — nunca atualizar, sempre criar novo registro.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class SavedPropertyRecord:
    id: UUID
    user_id: UUID
    trace_id: UUID | None
    property_data: dict             # snapshot JSONB completo da análise
    notes: str | None
    created_at: datetime


class SavedPropertyRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def save(
        self,
        user_id: str,
        property_data: dict,
        trace_id: str | None = None,
        notes: str | None = None,
    ) -> SavedPropertyRecord:
        """
        Salva um snapshot imutável do imóvel.
        NUNCA atualizar property_data — criar novo registro se necessário.
        """
        result = await (
            self._db.table("saved_properties")
            .insert({
                "user_id": user_id,
                "trace_id": trace_id,
                "property_data": property_data,
                "notes": notes,
            })
            .execute()
        )
        return self._map(result.data[0])

    async def list_by_user(
        self, user_id: str, limit: int = 50
    ) -> list[SavedPropertyRecord]:
        result = await (
            self._db.table("saved_properties")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    async def get_by_id(self, property_id: str) -> SavedPropertyRecord | None:
        result = await (
            self._db.table("saved_properties")
            .select("*")
            .eq("id", property_id)
            .maybe_single()
            .execute()
        )
        return self._map(result.data) if result.data else None

    async def delete(self, property_id: str) -> None:
        await (
            self._db.table("saved_properties")
            .delete()
            .eq("id", property_id)
            .execute()
        )

    async def update_notes(self, property_id: str, notes: str) -> None:
        """Apenas notes pode ser atualizado — property_data é IMUTÁVEL."""
        await (
            self._db.table("saved_properties")
            .update({"notes": notes})
            .eq("id", property_id)
            .execute()
        )

    def _map(self, row: dict) -> SavedPropertyRecord:
        return SavedPropertyRecord(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            trace_id=UUID(row["trace_id"]) if row.get("trace_id") else None,
            property_data=row["property_data"],
            notes=row.get("notes"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
