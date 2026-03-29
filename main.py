"""
IMOBILAY — End-to-End Pipeline Entry Point

Este módulo amarra as 3 camadas do sistema em uma execução sequencial.
Pode ser chamado pela API (api.py) ou via CLI.
"""

from __future__ import annotations

import logging
from uuid import uuid4

from layer_1_input.input_processor import InputProcessor
from layer_1_input.semantic_router import SemanticRouter
from layer_1_input.dag_resolver import DAGResolver
from layer_1_input.context_store import create_initial_context

from layer_2_orchestrator.orchestrator import Orchestrator
from layer_2_orchestrator.confidence_gate import ConfidenceGate
from layer_2_orchestrator.response_verbalizer import ResponseVerbalizer

from layer_3_learning.memory_manager import MemoryManager
from layer_3_learning.observability_layer import ObservabilityLayer

from models.context import ContextStore, UserProfile

logger = logging.getLogger(__name__)


class ImobilayPipeline:
    """Invólucro para o fluxo E2E."""

    def __init__(self):
        self.processor = InputProcessor()
        self.router = SemanticRouter()
        self.resolver = DAGResolver()
        self.orchestrator = Orchestrator()
        self.gate = ConfidenceGate()
        self.verbalizer = ResponseVerbalizer()
        
        # Camada 3 (Opcionais se banco for mocked)
        self.memory = MemoryManager()
        self.obs = ObservabilityLayer()

    async def initialize(self):
        """Prepara componentes assíncronos (como carregar embeddings de forma lazy)."""
        await self.router.initialize()

    async def run(
        self, 
        message: str, 
        user_id: str | None = None, 
        session_id: str | None = None
    ) -> tuple[str, ContextStore]:
        """
        Executa uma mensagem do usuário de ponta a ponta.
        Retorna a resposta (string verbalizada ou erro) e o contexto finalizado.
        """
        user_id = user_id or str(uuid4())
        session_id = session_id or str(uuid4())

        # 1. Recuperar memórias (Sessão / Usuário)
        # Opcional - injeção na mensagem caso precisemos de histórico
        session_state = await self.memory.get_session(session_id)
        user_profile = UserProfile(id=user_id)
        
        # 2. Layer 1: Input Processing
        processed_input = self.processor.process(
            raw_message=message,
            session_id=session_id,
            user_profile=user_profile,
        )
        
        # 3. Layer 1: Routing
        routing = await self.router.route(processed_input.message)
        
        # 4. Layer 1: DAG Resolution
        dag = self.resolver.resolve(routing)

        # 5. Layer 1: Setup inicial do Context
        initial_context = create_initial_context(processed_input)

        # 6. Layer 2: Orquestração (Agentes executam)
        # Se tivéssemos user profile em cache, injetaríamos aqui antes de passar pro orquestrador
        orch_result = await self.orchestrator.execute(dag, initial_context)
        
        # ContextData hidratado
        final_context = ContextStore.model_validate(orch_result.context_data)

        # 7. Layer 2: Confidence Gate
        gate_result = self.gate.validate(final_context)

        # 8. Layer 2: LLM Verbalization
        verbalized_response = ""
        # Sempre chamamos o GPT, o GateResult orienta se é erro de insuficiência ou resposta normal
        try:
            verbalized_response = await self.verbalizer.verbalize(final_context, gate_result)
        except Exception as e:
            logger.error(f"Erro na verbalização LLM: {e}")
            verbalized_response = "Tive um problema ao formular a resposta final. Por favor, tente novamente."

        # 9. Layer 3: Observabilidade
        await self.obs.record_execution(
            context=final_context,
            total_duration_ms=orch_result.total_duration_ms,
            gate_score=gate_result.score,
            intent=routing.primary_intent,
            confidence=routing.confidence,
            is_compound=routing.is_compound,
            agents_used=orch_result.agents_used,
            agents_failed=orch_result.agents_failed,
            agents_skipped=orch_result.agents_skipped,
            latency_per_agent=orch_result.latency_per_agent,
            dag_groups_count=len(dag.execution_groups)
        )
        
        # Salva state na session memory 
        await self.memory.save_session_state(session_id, final_context.model_dump(mode="json"))

        return verbalized_response, final_context


# Singleton
pipeline_instance = ImobilayPipeline()

async def get_pipeline() -> ImobilayPipeline:
    await pipeline_instance.initialize()
    return pipeline_instance

if __name__ == "__main__":
    import asyncio
    import sys

    # setup logging rápido
    logging.basicConfig(level=logging.INFO)

    async def shell():
        pipeline = await get_pipeline()
        msg = sys.argv[1] if len(sys.argv) > 1 else "quero kitnet perto da berrini"
        
        print(f"\nUsuário: {msg}")
        resp, ctx = await pipeline.run(msg)
        print(f"\nIMOBILAY: {resp}")
        print(f"\nImóveis extraídos: {len(ctx.properties)}")

    asyncio.run(shell())
