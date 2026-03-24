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

from database.client import get_system_client
from database.repositories import TraceRepository
from models.context import ContextStore
from models.routing import RoutineTrace

logger = logging.getLogger(__name__)


class ObservabilityLayer:
    """Coleta e armazena métricas e gera alertas no log."""

    def __init__(self, repository: TraceRepository | None = None):
        self._repo = repository or TraceRepository(get_system_client())

    async def record_execution(
        self,
        context: ContextStore,
        total_duration_ms: int,
        gate_score: float,
        intent: str | None,
        confidence: float | None
    ) -> RoutineTrace:
        """Processa e salva o trace de uma execução do pipeline completo."""
        
        # Extrair métricas dos agentes
        agent_metrics = {}
        for record in context.get_snapshot(context.version).get("patches", []):
            # O trace real vem do Orchestrator, então isso precisa ser repassado
            # Neste boilerplate usamos o record real que vamos montar
            pass

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

        # Tratar fallback rate (precisaria ser uma janela de 1h)
        # Aqui fazemos apenas o save do trace completo no banco (RoutineTrace ou ExecutionTrace)
        
        # Como o banco tem a tabela `execution_traces`, a interface exata do save é pelo repositorio
        # Vamos montar os metadados
        metadata = {
            "intent": intent,
            "confidence": confidence,
            "properties_found": properties_count,
            "valuations_calculated": valuation_count,
            "opportunities_detected": opportunities_count,
            "gate_score": gate_score,
            "total_ms": total_duration_ms
        }

        # Salvar async no banco
        try:
            return await self._repo.save_trace(
                trace_id=context.trace_id,
                session_id=context.input.session_id if context.input else None,
                user_id=context.user.id if context.user else None,
                total_duration_ms=total_duration_ms,
                gate_score=gate_score,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Erro ao salvar trace de execução: {e}")
            return None
