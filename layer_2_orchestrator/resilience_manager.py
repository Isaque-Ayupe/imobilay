"""
IMOBILAY — ResilienceManager

Gerencia retry, fallback e circuit breaker por agente.

Retry: máx 3, backoff 100ms → 400ms → 1600ms. Só em erros transitórios.
Fallback: cada agente declara fallback_value. Falha definitiva → usa fallback.
Circuit Breaker: CLOSED → OPEN (5 falhas em 60s) → HALF_OPEN (após 30s).
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Callable, Coroutine

from models.context import AgentError, ContextPatch, ContextStore, ErrorSeverity
from models.feedback import AgentHealthStats, AgentStatus, CircuitState


# ── Constantes ───────────────────────────────────────────────

MAX_RETRIES = 3
BACKOFF_BASE_MS = 100           # 100ms, 400ms, 1600ms
CIRCUIT_FAILURE_THRESHOLD = 5   # falhas para abrir
CIRCUIT_WINDOW_S = 60           # janela de observação
CIRCUIT_OPEN_DURATION_S = 30    # tempo em OPEN antes de HALF_OPEN


class ResilienceManager:
    """Gerencia resiliência por agente: retry, fallback e circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = CIRCUIT_FAILURE_THRESHOLD,
        open_duration_s: int = CIRCUIT_OPEN_DURATION_S,
        window_s: int = CIRCUIT_WINDOW_S,
        max_retries: int = MAX_RETRIES,
        backoff_base_ms: int = BACKOFF_BASE_MS,
    ):
        self._health: dict[str, AgentHealthStats] = {}
        self._failure_timestamps: dict[str, list[float]] = {}
        self._failure_threshold = failure_threshold
        self._open_duration_s = open_duration_s
        self._window_s = window_s
        self._max_retries = max_retries
        self._backoff_base_ms = backoff_base_ms

    async def call_with_resilience(
        self,
        agent_fn: Callable[..., Coroutine[Any, Any, ContextPatch]],
        agent_id: str,
        context: ContextStore,
        fallback_value: Any = None,
        output_field: str = "properties",
    ) -> tuple[ContextPatch | None, AgentStatus, AgentError | None]:
        """
        Executa agent_fn com retry, fallback e circuit breaker.

        Returns:
            (patch, status, error) — patch pode ser None se fallback também falha
        """
        health = self._get_or_create_health(agent_id)

        # ── Circuit Breaker: checar estado ──
        circuit = self._check_circuit(agent_id)
        if circuit == CircuitState.OPEN:
            # Retornar fallback imediatamente
            error = AgentError(
                agent_id=agent_id,
                error_type="CircuitBreakerOpen",
                message=f"Circuit breaker OPEN para {agent_id}. Usando fallback.",
                severity=ErrorSeverity.WARNING,
            )
            patch = ContextPatch(
                agent_id=agent_id,
                field=output_field,
                value=fallback_value,
            )
            health.total_fallbacks += 1
            return patch, AgentStatus.FALLBACK, error

        # ── Retry loop ──
        last_error = None
        for attempt in range(self._max_retries):
            try:
                health.total_calls += 1
                patch = await agent_fn(context)
                
                # Sucesso!
                health.last_success_at = datetime.utcnow()
                health.consecutive_failures = 0
                if health.circuit_state == CircuitState.HALF_OPEN:
                    health.circuit_state = CircuitState.CLOSED

                return patch, AgentStatus.SUCCESS, None

            except Exception as e:
                last_error = e
                is_transient = self._is_transient_error(e)

                if not is_transient:
                    # Erro de dados → fallback imediato, sem retry
                    break

                # Backoff exponencial: 100ms, 400ms, 1600ms
                if attempt < self._max_retries - 1:
                    delay_ms = self._backoff_base_ms * (4 ** attempt)
                    await asyncio.sleep(delay_ms / 1000)

        # ── Falha definitiva → fallback ──
        self._record_failure(agent_id)

        error = AgentError(
            agent_id=agent_id,
            error_type=type(last_error).__name__ if last_error else "UnknownError",
            message=str(last_error) if last_error else "Falha desconhecida",
            severity=ErrorSeverity.ERROR,
        )

        if fallback_value is not None:
            patch = ContextPatch(
                agent_id=agent_id,
                field=output_field,
                value=fallback_value,
            )
            health.total_fallbacks += 1
            return patch, AgentStatus.FALLBACK, error

        return None, AgentStatus.FAILED, error

    async def can_execute(self, agent_id: str) -> bool:
        return self._check_circuit(agent_id) != CircuitState.OPEN

    async def record_failure(self, agent_id: str) -> None:
        self._record_failure(agent_id)

    async def get_health_stats(self, agent_id: str) -> AgentHealthStats:
        self._check_circuit(agent_id)
        return self._get_or_create_health(agent_id)

    def get_circuit_state(self, agent_id: str) -> CircuitState:
        """Retorna o estado atual do circuit breaker para um agente."""
        return self._check_circuit(agent_id)

    def get_health_report(self) -> dict[str, AgentHealthStats]:
        """Retorna relatório de saúde de todos os agentes."""
        return dict(self._health)

    # ── Internos ─────────────────────────────────────────────

    def _get_or_create_health(self, agent_id: str) -> AgentHealthStats:
        if agent_id not in self._health:
            self._health[agent_id] = AgentHealthStats(agent_id=agent_id)
        return self._health[agent_id]

    def _check_circuit(self, agent_id: str) -> CircuitState:
        """Avalia e retorna o estado do circuit breaker."""
        health = self._get_or_create_health(agent_id)

        if health.circuit_state == CircuitState.CLOSED:
            return CircuitState.CLOSED

        if health.circuit_state == CircuitState.OPEN:
            # Verificar se já passou o tempo de cooldown
            if health.last_failure_at:
                elapsed = (datetime.utcnow() - health.last_failure_at).total_seconds()
                if elapsed >= self._open_duration_s:
                    health.circuit_state = CircuitState.HALF_OPEN
                    return CircuitState.HALF_OPEN
            return CircuitState.OPEN

        return health.circuit_state

    def _record_failure(self, agent_id: str):
        """Registra uma falha e avalia se deve abrir o circuit breaker."""
        health = self._get_or_create_health(agent_id)
        now = time.time()

        health.consecutive_failures += 1
        health.total_failures += 1
        health.last_failure_at = datetime.utcnow()

        # Manter timestamps de falhas recentes
        if agent_id not in self._failure_timestamps:
            self._failure_timestamps[agent_id] = []
        self._failure_timestamps[agent_id].append(now)

        # Limpar falhas fora da janela de observação
        cutoff = now - self._window_s
        self._failure_timestamps[agent_id] = [
            t for t in self._failure_timestamps[agent_id] if t > cutoff
        ]

        # Se atingiu o threshold na janela → abrir circuit breaker
        if len(self._failure_timestamps[agent_id]) >= self._failure_threshold:
            health.circuit_state = CircuitState.OPEN

    def _is_transient_error(self, error: Exception) -> bool:
        """Determina se o erro é transitório (vale retry)."""
        transient_types = (
            TimeoutError,
            ConnectionError,
            asyncio.TimeoutError,
        )
        if isinstance(error, transient_types):
            return True

        # HTTP 5xx → transitório
        error_msg = str(error).lower()
        if any(code in error_msg for code in ["500", "502", "503", "504", "timeout"]):
            return True

        return False
