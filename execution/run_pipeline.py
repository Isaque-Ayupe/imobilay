"""
IMOBILAY — Executar Pipeline Completo

Entry point para executar o pipeline de análise imobiliária via CLI.
Recebe uma mensagem do usuário, executa todas as camadas e retorna a resposta.

Uso:
    python execution/run_pipeline.py "quero um apartamento de 2 quartos em Goiânia"
    python execution/run_pipeline.py --user-id "uuid" --session-id "uuid" "mensagem"

Pré-requisitos:
    - Todos os módulos implementados (models, layer_1, layer_2, layer_3)
    - .env configurado
    - Supabase com tabelas criadas
    - Redis rodando (opcional — funciona sem, mas sem cache)
"""

import sys
import asyncio
import argparse
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


def parse_args():
    """Parse argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="IMOBILAY — Pipeline de Análise Imobiliária"
    )
    parser.add_argument(
        "message",
        type=str,
        help="Mensagem do usuário (ex: 'quero apartamento 2 quartos em Pinheiros')"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=str(uuid4()),
        help="UUID do usuário (default: gera novo)"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="UUID da sessão (default: cria nova)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Executar em modo mock (sem dependências externas)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar output detalhado de cada agente"
    )
    return parser.parse_args()


async def run_pipeline(message: str, user_id: str, session_id: str | None, mock: bool, verbose: bool):
    """
    Executa o pipeline completo:
    1. InputProcessor → ProcessedInput
    2. SemanticRouter → RoutingResult
    3. DAGResolver → ExecutionDAG
    4. Orchestrator → OrchestratorResult
    5. ConfidenceGate → GateResult
    6. ResponseVerbalizer → resposta em linguagem natural
    7. ObservabilityLayer → persistir trace
    """

    print(f"  Mensagem:   {message}")
    print(f"  User ID:    {user_id}")
    print(f"  Session ID: {session_id or '(nova sessão)'}")
    print(f"  Modo:       {'mock' if mock else 'produção'}")
    print()

    # TODO: Implementar quando todos os módulos estiverem prontos.
    #
    # Fluxo esperado:
    #
    # from layer_1_input.input_processor import InputProcessor
    # from layer_1_input.semantic_router import SemanticRouter
    # from layer_1_input.dag_resolver import DAGResolver
    # from layer_2_orchestrator.orchestrator import Orchestrator
    # from layer_2_orchestrator.confidence_gate import ConfidenceGate
    # from layer_2_orchestrator.response_verbalizer import ResponseVerbalizer
    # from layer_3_learning.observability_layer import ObservabilityLayer
    #
    # # Camada 1
    # processor = InputProcessor()
    # processed = processor.process(message, session_id, user_id)
    # print(f"  ✓ Input processado (trace_id: {processed.trace_id})")
    #
    # router = SemanticRouter()
    # routing = await router.route(processed)
    # print(f"  ✓ Intent: {routing.primary_intent} (confiança: {routing.confidence:.2f})")
    #
    # dag = DAGResolver().resolve(routing)
    # print(f"  ✓ DAG montado: {dag.estimated_steps} passos")
    #
    # # Camada 2
    # orchestrator = Orchestrator()
    # result = await orchestrator.execute(dag, context)
    # print(f"  ✓ Pipeline executado em {result.total_duration_ms}ms")
    #
    # gate = ConfidenceGate().validate(result.context)
    # print(f"  ✓ Confidence gate: {gate.recommendation} (score: {gate.score:.2f})")
    #
    # if gate.passed:
    #     verbalizer = ResponseVerbalizer()
    #     response = await verbalizer.verbalize(result.context, gate)
    #     print(f"\n{'='*50}")
    #     print(response)
    # else:
    #     print(f"\n⚠ Dados insuficientes: {gate.missing_fields}")

    print("⚠ Pipeline ainda não implementado.")
    print("  → Siga a ordem dos directives (01 a 08) para implementar cada módulo.")
    print("  → Execute com --mock para testar com dados fake quando disponível.")


def main():
    args = parse_args()

    print("=" * 50)
    print("IMOBILAY — Pipeline de Análise Imobiliária")
    print("=" * 50)
    print()

    asyncio.run(run_pipeline(
        message=args.message,
        user_id=args.user_id,
        session_id=args.session_id,
        mock=args.mock,
        verbose=args.verbose,
    ))


if __name__ == "__main__":
    main()
