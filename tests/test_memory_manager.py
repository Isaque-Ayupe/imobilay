import pytest
from layer_3_learning.memory_manager import MemoryManager

@pytest.mark.asyncio
async def test_memory_fallback():
    # Testa que o MemoryManager funciona com cache local se redis estiver ausente
    manager = MemoryManager()
    await manager.set_cached_result("test_key", {"data": 123}, 10)
    
    val = await manager.get_cached_result("test_key")
    assert val is not None
    assert val["data"] == 123
