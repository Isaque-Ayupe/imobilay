"""
IMOBILAY — ObservabilityLayer

Coleta métricas por execução do pipeline e gera alertas automáticos.
Persiste o trace completo no banco de dados via TraceRepository.

Alertas:
  - latencia_total_ms > 8000
  - taxa_fallback > 0.3 em 10 execuções (TODO)
  - confidence_gate_score < 0.5 repetitivo (TODO)
"""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from database.client import get_system_client
from database.repositories.trace_repository import TraceRepository, TraceRecord
from models.context import ContextStore

logger = logging.getLogger(__name__)


class ObservabilityLayer:
    """Coleta e armazena métricas e gera alertas no log."""

    def __init__(self, repository: TraceRepository | None = None):
        self._repo = repository

    async def _get_repo(self) -> TraceRepository:
        if self._repo is None:
            self._repo = TraceRepository(await get_system_client())
        return self._repo

    async def record_execution(
        self,
        context: ContextStore,
        total_duration_ms: int,
        gate_score: float,
        intent: str | None,
        confidence: float | None,
        is_compound: bool = False,
        agents_used: list[str] | None = None,
        agents_failed: list[str] | None = None,
        agents_skipped: list[str] | None = None,
        latency_per_agent: dict | None = None,
        dag_groups_count: int | None = None
    ) -> None:
        """Processa e salva o trace de uma execução do pipeline completo."""
        await self._ensure_repo()
        
        properties_count = len(context.properties)
        valuation_count = len(context.analysis.valuation)
        opportunities_count = len(context.analysis.opportunities)

        # Checar alertas
        if total_duration_ms > 8000:
            logger.warning(
                f"[ALERT] High Latency: Trace {context.trace_id} demorou {total_duration_ms}ms"
            )

        if gate_score < 0.5:
            logger.warning(
                f"[ALERT] Low Confidence: Trace {context.trace_id} teve gate score {gate_score:.2f}"
            )

        # Montar o TraceRecord para o repositório
        trace_record = TraceRecord(
            trace_id=UUID(context.trace_id) if isinstance(context.trace_id, str) else context.trace_id,
            session_id=UUID(context.input.session_id) if context.input and context.input.session_id else None,
            user_id=UUID(context.user.id) if context.user and context.user.id else None,
            intent_detected=intent,
            intent_confidence=confidence,
            is_compound_intent=is_compound,
            confidence_gate_score=gate_score,
            confidence_gate_passed=gate_score >= 0.7, # Threshold padrão do ConfidenceGate
            properties_found=properties_count,
            properties_with_valuation=valuation_count,
            opportunities_detected=opportunities_count,
            latency_total_ms=total_duration_ms,
            latency_per_agent=latency_per_agent or {},
            agents_used=agents_used or [],
            agents_failed=agents_failed or [],
            agents_skipped=agents_skipped or [],
            dag_execution_groups=dag_groups_count,
            created_at=datetime.now()
        )

        # Salvar async no banco
        try:
            repo = await self._get_repo()
            await repo.save(trace_record)
        except Exception as e:
            logger.error(f"Erro ao salvar trace de execução: {e}")
