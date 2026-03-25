import pytest
from layer_1_input.semantic_router import SemanticRouter

@pytest.mark.asyncio
async def test_semantic_router_initialization():
    router = SemanticRouter()
    await router.initialize()
    assert router._model is not None or router._use_fallback is True

@pytest.mark.asyncio
async def test_semantic_router_route():
    router = SemanticRouter()
    await router.initialize()
    result = await router.route("quero investir em um apartamento")
    
    assert result.primary_intent is not None
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0
