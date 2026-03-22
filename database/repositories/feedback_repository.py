"""
IMOBILAY — FeedbackRepository

Persistência de feedback_records (sinais de qualidade — Camada 3).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class FeedbackRecordRow:
    id: UUID
    trace_id: UUID | None
    user_id: UUID | None
    session_id: UUID | None
    explicit_rating: int | None
    implicit_signal: str | None
    intent_original: str | None
    agents_used: list[str]
    agents_failed: list[str]
    total_duration_ms: int | None
    created_at: datetime


class FeedbackRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def save(
        self,
        trace_id: str,
        user_id: str,
        session_id: str | None = None,
        explicit_rating: int | None = None,
        implicit_signal: str | None = None,
        intent_original: str | None = None,
        agents_used: list[str] | None = None,
        agents_failed: list[str] | None = None,
        total_duration_ms: int | None = None,
    ) -> FeedbackRecordRow:
        result = await (
            self._db.table("feedback_records")
            .insert({
                "trace_id": trace_id,
                "user_id": user_id,
                "session_id": session_id,
                "explicit_rating": explicit_rating,
                "implicit_signal": implicit_signal,
                "intent_original": intent_original,
                "agents_used": agents_used or [],
                "agents_failed": agents_failed or [],
                "total_duration_ms": total_duration_ms,
            })
            .execute()
        )
        return self._map(result.data[0])

    async def update_explicit_rating(self, trace_id: str, rating: int) -> None:
        """Atualiza rating explícito após o usuário avaliar a resposta."""
        await (
            self._db.table("feedback_records")
            .update({"explicit_rating": rating})
            .eq("trace_id", trace_id)
            .execute()
        )

    async def get_by_trace_id(self, trace_id: str) -> FeedbackRecordRow | None:
        result = await (
            self._db.table("feedback_records")
            .select("*")
            .eq("trace_id", trace_id)
            .maybe_single()
            .execute()
        )
        return self._map(result.data) if result.data else None

    async def get_recent_by_user(
        self, user_id: str, limit: int = 50
    ) -> list[FeedbackRecordRow]:
        result = await (
            self._db.table("feedback_records")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    def _map(self, row: dict) -> FeedbackRecordRow:
        return FeedbackRecordRow(
            id=UUID(row["id"]),
            trace_id=UUID(row["trace_id"]) if row.get("trace_id") else None,
            user_id=UUID(row["user_id"]) if row.get("user_id") else None,
            session_id=UUID(row["session_id"]) if row.get("session_id") else None,
            explicit_rating=row.get("explicit_rating"),
            implicit_signal=row.get("implicit_signal"),
            intent_original=row.get("intent_original"),
            agents_used=row.get("agents_used") or [],
            agents_failed=row.get("agents_failed") or [],
            total_duration_ms=row.get("total_duration_ms"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
