"""
IMOBILAY — TraceRepository

Persistência de execution_traces (rastreabilidade do pipeline).
Usado pela ObservabilityLayer e RouterFeedbackLoop.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class TraceRecord:
    trace_id: UUID
    session_id: UUID | None
    user_id: UUID | None
    intent_detected: str | None
    intent_confidence: float | None
    is_compound_intent: bool
    confidence_gate_score: float | None
    confidence_gate_passed: bool | None
    properties_found: int
    properties_with_valuation: int
    opportunities_detected: int
    latency_total_ms: int | None
    latency_per_agent: dict | None
    agents_used: list[str]
    agents_failed: list[str]
    agents_skipped: list[str]
    dag_execution_groups: int | None
    created_at: datetime


class TraceRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def save(self, trace: TraceRecord) -> None:
        """
        Persiste o ExecutionTrace ao final do pipeline.
        Chamado pela ObservabilityLayer após todas as fases concluírem.
        """
        await (
            self._db.table("execution_traces")
            .insert({
                "trace_id":                 str(trace.trace_id),
                "session_id":               str(trace.session_id) if trace.session_id else None,
                "user_id":                  str(trace.user_id) if trace.user_id else None,
                "intent_detected":          trace.intent_detected,
                "intent_confidence":        trace.intent_confidence,
                "is_compound_intent":       trace.is_compound_intent,
                "confidence_gate_score":    trace.confidence_gate_score,
                "confidence_gate_passed":   trace.confidence_gate_passed,
                "properties_found":         trace.properties_found,
                "properties_with_valuation": trace.properties_with_valuation,
                "opportunities_detected":   trace.opportunities_detected,
                "latency_total_ms":         trace.latency_total_ms,
                "latency_per_agent":        trace.latency_per_agent,
                "agents_used":              trace.agents_used,
                "agents_failed":            trace.agents_failed,
                "agents_skipped":           trace.agents_skipped,
                "dag_execution_groups":     trace.dag_execution_groups,
            })
            .execute()
        )

    async def get_by_trace_id(self, trace_id: str) -> TraceRecord | None:
        result = await (
            self._db.table("execution_traces")
            .select("*")
            .eq("trace_id", trace_id)
            .maybe_single()
            .execute()
        )
        return self._map(result.data) if result.data else None

    async def get_recent_by_user(
        self, user_id: str, limit: int = 100
    ) -> list[TraceRecord]:
        """Usado pelo RouterFeedbackLoop para calcular métricas por intent."""
        result = await (
            self._db.table("execution_traces")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    async def get_for_feedback_cycle(self, limit: int = 100) -> list[TraceRecord]:
        """
        Usado pelo RouterFeedbackLoop a cada 100 execuções.
        Busca traces recentes de todos os usuários para recalcular pesos.
        Requer service_role (sem filtro de user_id).
        """
        result = await (
            self._db.table("execution_traces")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    def _map(self, row: dict) -> TraceRecord:
        return TraceRecord(
            trace_id=UUID(row["trace_id"]),
            session_id=UUID(row["session_id"]) if row.get("session_id") else None,
            user_id=UUID(row["user_id"]) if row.get("user_id") else None,
            intent_detected=row.get("intent_detected"),
            intent_confidence=row.get("intent_confidence"),
            is_compound_intent=row.get("is_compound_intent", False),
            confidence_gate_score=row.get("confidence_gate_score"),
            confidence_gate_passed=row.get("confidence_gate_passed"),
            properties_found=row.get("properties_found", 0),
            properties_with_valuation=row.get("properties_with_valuation", 0),
            opportunities_detected=row.get("opportunities_detected", 0),
            latency_total_ms=row.get("latency_total_ms"),
            latency_per_agent=row.get("latency_per_agent"),
            agents_used=row.get("agents_used") or [],
            agents_failed=row.get("agents_failed") or [],
            agents_skipped=row.get("agents_skipped") or [],
            dag_execution_groups=row.get("dag_execution_groups"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
