"""
IMOBILAY — UserRepository

CRUD para a tabela user_profiles.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class UserProfileRecord:
    id: UUID
    name: str
    plan: str
    analysis_count: int
    created_at: datetime
    updated_at: datetime


class UserRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def get_by_id(self, user_id: str) -> UserProfileRecord | None:
        result = await (
            self._db.table("user_profiles")
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        return self._map(result.data) if result.data else None

    async def create(self, user_id: str, name: str, plan: str = "free") -> UserProfileRecord:
        result = await (
            self._db.table("user_profiles")
            .insert({"id": user_id, "name": name, "plan": plan})
            .execute()
        )
        return self._map(result.data[0])

    async def update_plan(self, user_id: str, plan: str) -> None:
        await (
            self._db.table("user_profiles")
            .update({"plan": plan})
            .eq("id", user_id)
            .execute()
        )

    async def increment_analysis_count(self, user_id: str) -> None:
        await self._db.rpc(
            "increment_analysis_count",
            {"p_user_id": user_id}
        ).execute()

    def _map(self, row: dict) -> UserProfileRecord:
        return UserProfileRecord(
            id=UUID(row["id"]),
            name=row["name"],
            plan=row["plan"],
            analysis_count=row["analysis_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
