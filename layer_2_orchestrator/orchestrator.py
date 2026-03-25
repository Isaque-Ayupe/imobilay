"""
IMOBILAY — Orchestrator (Supervisor Agent)

Executa o ExecutionDAG coordenando agentes em paralelo/sequencial.
Gerencia o ContextStore, aplica patches e aciona o ResilienceManager.

Fluxo:
1. Recebe DAG + ContextStore da Camada 1
2. Para cada ExecutionGroup: PARALLEL → asyncio.gather() | SEQUENTIAL → em ordem
3. Após cada agente: context.apply_patch(patch)
4. Em falha: aciona ResilienceManager (retry + fallback)
5. Ao final: retorna OrchestratorResult
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime

from models.context import ContextStore
from models.routing import ExecutionDAG, ExecutionType
from models.feedback import AgentExecutionRecord, AgentStatus, OrchestratorResult

from layer_2_orchestrator.resilience_manager import ResilienceManager
from layer_2_orchestrator.agents.base_agent import BaseAgent
from layer_2_orchestrator.agents.web_scraper_agent import WebScraperAgent
from layer_2_orchestrator.agents.normalize_agent import NormalizeAgent
from layer_2_orchestrator.agents.location_insights_agent import LocationInsightsAgent
from layer_2_orchestrator.agents.valuation_agent import ValuationAgent
from layer_2_orchestrator.agents.investment_analysis_agent import InvestmentAnalysisAgent
from layer_2_orchestrator.agents.opportunity_detection_agent import OpportunityDetectionAgent
from layer_2_orchestrator.agents.compare_properties_agent import ComparePropertiesAgent


# ── Registro de agentes ──────────────────────────────────────

AGENT_REGISTRY: dict[str, BaseAgent] = {
    "web_scraper":          WebScraperAgent(),
    "normalize":            NormalizeAgent(),
    "location_insights":    LocationInsightsAgent(),
    "valuation":            ValuationAgent(),
    "investment_analysis":  InvestmentAnalysisAgent(),
    "opportunity_detection": OpportunityDetectionAgent(),
    "compare_properties":   ComparePropertiesAgent(),
}


class Orchestrator:
    """
    Supervisor Agent: executa o DAG, coordena agentes e gerencia estado.
    """

    def __init__(self, resilience: ResilienceManager | None = None):
        self._resilience = resilience or ResilienceManager()

    async def execute(
        self, dag: ExecutionDAG, context: ContextStore
    ) -> OrchestratorResult:
        """
        Executa o DAG completo com paralelismo real.

        Args:
            dag: ExecutionDAG do DAGResolver
            context: ContextStore inicial (imutável)

        Returns:
            OrchestratorResult com contexto atualizado e trace de execução
        """
        start_time = time.time()
        records: list[AgentExecutionRecord] = []
        agents_failed: list[str] = []
        agents_skipped: list[str] = []

        current_context = context

        for group in dag.execution_groups:
            if group.execution_type == ExecutionType.PARALLEL:
                # Executar agentes em paralelo
                tasks = []
                for node in group.nodes:
                    agent = AGENT_REGISTRY.get(node.agent_id)
                    if agent is None:
                        agents_skipped.append(node.agent_id)
                        continue
                    tasks.append(
                        self._execute_agent(agent, current_context)
                    )

                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in results:
                        if isinstance(result, Exception):
                            continue
                        record, new_context = result
                        records.append(record)
                        if new_context is not None:
                            current_context = new_context
                        if record.status == AgentStatus.FAILED:
                            agents_failed.append(record.agent_id)

            else:
                # Executar sequencialmente
                for node in group.nodes:
                    agent = AGENT_REGISTRY.get(node.agent_id)
                    if agent is None:
                        agents_skipped.append(node.agent_id)
                        continue

                    result = await self._execute_agent(agent, current_context)
                    record, new_context = result
                    records.append(record)
                    if new_context is not None:
                        current_context = new_context
                    if record.status == AgentStatus.FAILED:
                        agents_failed.append(record.agent_id)

        total_ms = int((time.time() - start_time) * 1000)

        # Coletar métricas adicionais para o OrchestratorResult
        agents_used = [r.agent_id for r in records if r.status == AgentStatus.SUCCESS or r.status == AgentStatus.FALLBACK]
        latency_per_agent = {r.agent_id: r.duration_ms for r in records}

        return OrchestratorResult(
            context_data=current_context.model_dump(),
            execution_trace=records,
            total_duration_ms=total_ms,
            agents_used=agents_used,
            agents_failed=agents_failed,
            agents_skipped=agents_skipped,
            latency_per_agent=latency_per_agent
        )

    async def _execute_agent(
        self, agent: BaseAgent, context: ContextStore
    ) -> tuple[AgentExecutionRecord, ContextStore | None]:
        """Executa um agente com resiliência e retorna o record + novo contexto."""
        start = time.time()
        started_at = datetime.utcnow()

        # Validar input
        if not agent.validate_input(context):
            return (
                AgentExecutionRecord(
                    agent_id=agent.agent_id,
                    status=AgentStatus.SKIPPED,
                    duration_ms=0,
                    error="Input inválido ou insuficiente",
                    started_at=started_at,
                    finished_at=datetime.utcnow()
                ),
                None,
            )

        # Executar com resiliência
        patch, status, error = await self._resilience.call_with_resilience(
            agent_fn=agent.execute,
            agent_id=agent.agent_id,
            context=context,
            fallback_value=agent.fallback_value,
            output_field=agent._output_field,
        )

        duration_ms = int((time.time() - start) * 1000)

        # Aplicar patch no context
        new_context = None
        patch_applied = False
        if patch is not None:
            try:
                new_context = context.apply_patch(
                    agent_id=patch.agent_id,
                    field=patch.field,
                    value=patch.value,
                )
                patch_applied = True
            except Exception:
                pass

        # Se houve erro, adicionar ao context
        if error and new_context:
            new_context = new_context.add_error(error)
        elif error and not new_context:
            new_context = context.add_error(error)

        record = AgentExecutionRecord(
            agent_id=agent.agent_id,
            status=status,
            duration_ms=duration_ms,
            error=str(error.message) if error else None,
            patch_applied=patch_applied,
            fallback_used=status == AgentStatus.FALLBACK,
            started_at=started_at,
            finished_at=datetime.utcnow(),
        )

        return record, new_context
