import pytest
from layer_2_orchestrator.confidence_gate import ConfidenceGate
from models.context import ContextStore, GateRecommendation

def test_confidence_gate_empty():
    gate = ConfidenceGate()
    ctx = ContextStore()
    
    result = gate.validate(ctx)
    assert result.passed is False
    assert result.recommendation == GateRecommendation.RETURN_LIMITATION
    assert "properties" in result.missing_fields
