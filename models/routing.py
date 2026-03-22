"""
IMOBILAY — Models de Roteamento e DAG

Tipos para o SemanticRouter e DAGResolver:
classificação de intents, nós do grafo e grupos de execução.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────


class IntentType(str, Enum):
    BUSCAR_IMOVEIS = "buscar_imoveis"
    ANALISAR_IMOVEL = "analisar_imovel"
    INVESTIMENTO = "investimento"
    REFINAR_BUSCA = "refinar_busca"


class EdgeType(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    CONDITIONAL = "CONDITIONAL"


class ExecutionType(str, Enum):
    PARALLEL = "PARALLEL"
    SEQUENTIAL = "SEQUENTIAL"


# ── Models ───────────────────────────────────────────────────


class RoutingResult(BaseModel):
    """Resultado da classificação de intent pelo SemanticRouter."""

    primary_intent: str                      # intent principal detectado
    secondary_intent: str | None = None      # intent secundário (para compostos)
    confidence: float = Field(ge=0, le=1)    # confiança do intent principal
    is_compound: bool = False                # True se dois intents > threshold
    raw_scores: dict[str, float] = Field(default_factory=dict)  # scores de todos os intents


class DAGNode(BaseModel):
    """Nó no grafo de execução — representa um agente a ser executado."""

    id: str                                  # identificador único do nó
    agent_id: str                            # ID do agente (ex: "web_scraper", "valuation")
    dependencies: list[str] = Field(default_factory=list)  # IDs de nós que devem completar antes
    condition: str | None = None             # predicado para nós condicionais (ex: "properties.length > 0")


class DAGEdge(BaseModel):
    """Aresta no grafo de execução — relação entre dois nós."""

    from_node: str                           # ID do nó de origem
    to_node: str                             # ID do nó de destino
    edge_type: EdgeType = EdgeType.SEQUENTIAL


class ExecutionGroup(BaseModel):
    """
    Grupo de nós que podem ser executados juntos.
    PARALLEL: todos executam ao mesmo tempo via asyncio.gather()
    SEQUENTIAL: executam em ordem dentro do grupo
    """

    nodes: list[DAGNode] = Field(default_factory=list)
    execution_type: ExecutionType = ExecutionType.SEQUENTIAL
    order: int = 0                           # ordem de execução do grupo dentro do DAG


class ExecutionDAG(BaseModel):
    """
    Grafo Acíclico Dirigido (DAG) de execução.
    Gerado pelo DAGResolver a partir do RoutingResult.
    """

    nodes: list[DAGNode] = Field(default_factory=list)
    edges: list[DAGEdge] = Field(default_factory=list)
    execution_groups: list[ExecutionGroup] = Field(default_factory=list)
    estimated_steps: int = 0
    intent: str = ""                         # intent que gerou este DAG

    @property
    def agent_ids(self) -> list[str]:
        """Retorna lista de todos os agent_ids no DAG."""
        return [node.agent_id for node in self.nodes]

    @property
    def parallel_groups(self) -> list[ExecutionGroup]:
        """Retorna apenas os grupos paralelos."""
        return [g for g in self.execution_groups if g.execution_type == ExecutionType.PARALLEL]
