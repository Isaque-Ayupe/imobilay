"""
IMOBILAY — BaseAgent (Contrato ABC)

Todas os agentes especializados herdam desta classe.
Cada agente declara:
  - agent_id: identificador único
  - fallback_value: valor a usar quando falha definitivamente
  - execute(): lê do context, retorna ContextPatch com resultado
  - validate_input(): verifica se o context tem o mínimo necessário
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models.context import ContextPatch, ContextStore


class BaseAgent(ABC):
    """Contrato base para todos os agentes especializados."""

    agent_id: str = "base"
    fallback_value: Any = None

    @abstractmethod
    async def execute(self, context: ContextStore) -> ContextPatch:
        """
        Executa a lógica do agente.

        Args:
            context: estado compartilhado atual (imutável)

        Returns:
            ContextPatch descrevendo a escrita a ser aplicada
        """
        ...

    def validate_input(self, context: ContextStore) -> bool:
        """
        Verifica se o context tem os dados mínimos para este agente executar.
        Override nas subclasses para validação específica.
        """
        return True

    def get_fallback_patch(self) -> ContextPatch:
        """Retorna patch com fallback_value quando o agente falha."""
        return ContextPatch(
            agent_id=self.agent_id,
            field=self._output_field,
            value=self.fallback_value,
        )

    @property
    def _output_field(self) -> str:
        """Campo do ContextStore que este agente escreve. Override nas subclasses."""
        return "properties"
