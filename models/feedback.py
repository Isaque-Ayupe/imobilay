"""
IMOBILAY — Models de Feedback e Observabilidade

Tipos para rastreabilidade de execução, feedback do usuário,
métricas e traces completos do pipeline.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from models.context import GateResult
from models.routing import ExecutionDAG


# ── Enums ────────────────────────────────────────────────────


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    FALLBACK = "fallback"


class ImplicitSignal(str, Enum):
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNCERTAIN = "uncertain"


# ── Models ───────────────────────────────────────────────────


class AgentExecutionRecord(BaseModel):
    """Registro de execução de um agente individual."""

    agent_id: str
    status: AgentStatus = AgentStatus.PENDING
    duration_ms: int = 0
    error: str | None = None                 # mensagem de erro se falhou
    retry_count: int = 0                     # quantas vezes retentou
    patch_applied: bool = False              # se o patch foi aplicado no ContextStore
    fallback_used: bool = False              # se usou valor de fallback
    started_at: datetime | None = None
    finished_at: datetime | None = None


class FeedbackRecord(BaseModel):
    """Registro de feedback do usuário (explícito e implícito)."""

    trace_id: str
    session_id: str
    user_id: str
    explicit_rating: int | None = Field(default=None, ge=1, le=5)   # 1-5 do usuário
    implicit_signal: ImplicitSignal = ImplicitSignal.UNCERTAIN
    intent_original: str | None = None       # intent que gerou a execução
    agents_used: list[str] = Field(default_factory=list)
    agents_failed: list[str] = Field(default_factory=list)
    total_duration_ms: int | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionMetrics(BaseModel):
    """Métricas coletadas por execução — usadas pela ObservabilityLayer."""

    latencia_total_ms: int = 0
    latencia_por_agent: dict[str, int] = Field(default_factory=dict)   # ex: {"web_scraper": 1200}
    taxa_fallback_por_agent: dict[str, float] = Field(default_factory=dict)  # acumulado por janela
    confidence_gate_score: float = 0.0
    intent_detectado: str = ""
    intent_confidence: float = 0.0
    properties_encontradas: int = 0
    properties_com_valuation: int = 0
    oportunidades_detectadas: int = 0


class OrchestratorResult(BaseModel):
    """Resultado completo da execução do Orchestrator."""

    context_data: dict = Field(default_factory=dict)    # ContextStore serializado
    execution_trace: list[AgentExecutionRecord] = Field(default_factory=list)
    total_duration_ms: int = 0
    agents_failed: list[str] = Field(default_factory=list)
    agents_skipped: list[str] = Field(default_factory=list)


class ExecutionTrace(BaseModel):
    """
    Trace completo de uma execução do pipeline.
    Gerado pela ObservabilityLayer e persistido via TraceRepository.
    """

    trace_id: str
    session_id: str | None = None
    user_id: str | None = None
    dag_resolved: ExecutionDAG | None = None
    agent_records: list[AgentExecutionRecord] = Field(default_factory=list)
    context_patches_count: int = 0
    gate_result: GateResult | None = None
    feedback: FeedbackRecord | None = None
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Circuit Breaker State ────────────────────────────────────


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class AgentHealthStats(BaseModel):
    """Estatísticas de saúde de um agente — usadas pelo ResilienceManager."""

    agent_id: str
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    total_calls: int = 0
    total_failures: int = 0
    total_fallbacks: int = 0
    last_failure_at: datetime | None = None
    last_success_at: datetime | None = None
    avg_latency_ms: float = 0.0
