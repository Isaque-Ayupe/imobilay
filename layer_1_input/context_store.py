"""
IMOBILAY — SharedContextStore (Camada 1)

Re-exporta o ContextStore de models/context.py e
adiciona helpers de fábrica para criação do contexto inicial.

O ContextStore em si está em models/context.py —
aqui apenas facilitamos o acesso para a Camada 1.
"""

from models.context import (
    ContextStore,
    ProcessedInput,
    create_initial_context,
)

__all__ = [
    "ContextStore",
    "ProcessedInput",
    "create_initial_context",
]
