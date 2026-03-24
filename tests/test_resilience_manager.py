import pytest
from layer_2_orchestrator.resilience_manager import ResilienceManager
from models.feedback import CircuitState

@pytest.mark.asyncio
async def test_circuit_breaker_flow():
    manager = ResilienceManager(failure_threshold=3)
    
    # 3 falhas abrem o circuito
    await manager.record_failure("test_agent")
    await manager.record_failure("test_agent")
    await manager.record_failure("test_agent")
    
    stats = await manager.get_health_stats("test_agent")
    assert stats.circuit_state == CircuitState.OPEN
    
    # Se está OPEN e chamamos, ele é barrado
    allowed = await manager.can_execute("test_agent")
    assert not allowed
