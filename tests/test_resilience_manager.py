import pytest
from layer_2_orchestrator.resilience_manager import ResilienceManager
from models.feedback import CircuitState

@pytest.mark.asyncio
async def test_circuit_breaker_flow():
    manager = ResilienceManager()
    
    # Simula 5 falhas rápidas (threshold padrão)
    manager._record_failure("test_agent")
    manager._record_failure("test_agent")
    manager._record_failure("test_agent")
    manager._record_failure("test_agent")
    manager._record_failure("test_agent")
    
    stats = manager.get_circuit_state("test_agent")
    from models.feedback import CircuitState
    assert stats == CircuitState.OPEN
