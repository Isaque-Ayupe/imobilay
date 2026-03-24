import pytest
from layer_2_orchestrator.orchestrator import Orchestrator
from layer_1_input.dag_resolver import DAGResolver
from models.routing import RoutingResult
from models.context import ContextStore

@pytest.mark.asyncio
async def test_orchestratorEmptyDag():
    orch = Orchestrator()
    dag = DAGResolver().resolve(RoutingResult(message="oi", primary_intent="greeting", confidence=0.9))
    ctx = ContextStore()

    result = await orch.execute(dag, ctx)
    assert result.total_duration_ms >= 0
    assert len(result.execution_trace) == 0
