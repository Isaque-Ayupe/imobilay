"""
IMOBILAY — DAGResolver (Camada 1)

Converte o RoutingResult em um ExecutionDAG — grafo de agentes
a serem executados com dependências explícitas.

Mapeamento fixo de intents → DAGs:
  buscar_imoveis:   web_scraper → normalize → [location_insights, valuation] → compare_properties
  analisar_imovel:  location_insights → valuation → investment_analysis
  investimento:     web_scraper → normalize → [location_insights, valuation] → investment_analysis → opportunity_detection → compare_properties
  refinar_busca:    web_scraper → normalize → compare_properties
"""

from __future__ import annotations

from models.routing import (
    DAGEdge,
    DAGNode,
    EdgeType,
    ExecutionDAG,
    ExecutionGroup,
    ExecutionType,
    RoutingResult,
)


# ── DAG Templates ────────────────────────────────────────────

def _dag_buscar_imoveis() -> tuple[list[DAGNode], list[DAGEdge], list[ExecutionGroup]]:
    nodes = [
        DAGNode(id="n1", agent_id="web_scraper", dependencies=[]),
        DAGNode(id="n2", agent_id="normalize", dependencies=["n1"]),
        DAGNode(id="n3", agent_id="location_insights", dependencies=["n2"]),
        DAGNode(id="n4", agent_id="valuation", dependencies=["n2"]),
        DAGNode(id="n5", agent_id="compare_properties", dependencies=["n3", "n4"]),
    ]
    edges = [
        DAGEdge(from_node="n1", to_node="n2", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n2", to_node="n3", edge_type=EdgeType.PARALLEL),
        DAGEdge(from_node="n2", to_node="n4", edge_type=EdgeType.PARALLEL),
        DAGEdge(from_node="n3", to_node="n5", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n4", to_node="n5", edge_type=EdgeType.SEQUENTIAL),
    ]
    groups = [
        ExecutionGroup(nodes=[nodes[0]], execution_type=ExecutionType.SEQUENTIAL, order=0),
        ExecutionGroup(nodes=[nodes[1]], execution_type=ExecutionType.SEQUENTIAL, order=1),
        ExecutionGroup(nodes=[nodes[2], nodes[3]], execution_type=ExecutionType.PARALLEL, order=2),
        ExecutionGroup(nodes=[nodes[4]], execution_type=ExecutionType.SEQUENTIAL, order=3),
    ]
    return nodes, edges, groups


def _dag_analisar_imovel() -> tuple[list[DAGNode], list[DAGEdge], list[ExecutionGroup]]:
    nodes = [
        DAGNode(id="n1", agent_id="location_insights", dependencies=[]),
        DAGNode(id="n2", agent_id="valuation", dependencies=["n1"]),
        DAGNode(id="n3", agent_id="investment_analysis", dependencies=["n2"]),
    ]
    edges = [
        DAGEdge(from_node="n1", to_node="n2", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n2", to_node="n3", edge_type=EdgeType.SEQUENTIAL),
    ]
    groups = [
        ExecutionGroup(nodes=[nodes[0]], execution_type=ExecutionType.SEQUENTIAL, order=0),
        ExecutionGroup(nodes=[nodes[1]], execution_type=ExecutionType.SEQUENTIAL, order=1),
        ExecutionGroup(nodes=[nodes[2]], execution_type=ExecutionType.SEQUENTIAL, order=2),
    ]
    return nodes, edges, groups


def _dag_investimento() -> tuple[list[DAGNode], list[DAGEdge], list[ExecutionGroup]]:
    nodes = [
        DAGNode(id="n1", agent_id="web_scraper", dependencies=[]),
        DAGNode(id="n2", agent_id="normalize", dependencies=["n1"]),
        DAGNode(id="n3", agent_id="location_insights", dependencies=["n2"]),
        DAGNode(id="n4", agent_id="valuation", dependencies=["n2"]),
        DAGNode(id="n5", agent_id="investment_analysis", dependencies=["n3", "n4"]),
        DAGNode(id="n6", agent_id="opportunity_detection", dependencies=["n5"]),
        DAGNode(id="n7", agent_id="compare_properties", dependencies=["n6"]),
    ]
    edges = [
        DAGEdge(from_node="n1", to_node="n2", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n2", to_node="n3", edge_type=EdgeType.PARALLEL),
        DAGEdge(from_node="n2", to_node="n4", edge_type=EdgeType.PARALLEL),
        DAGEdge(from_node="n3", to_node="n5", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n4", to_node="n5", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n5", to_node="n6", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n6", to_node="n7", edge_type=EdgeType.SEQUENTIAL),
    ]
    groups = [
        ExecutionGroup(nodes=[nodes[0]], execution_type=ExecutionType.SEQUENTIAL, order=0),
        ExecutionGroup(nodes=[nodes[1]], execution_type=ExecutionType.SEQUENTIAL, order=1),
        ExecutionGroup(nodes=[nodes[2], nodes[3]], execution_type=ExecutionType.PARALLEL, order=2),
        ExecutionGroup(nodes=[nodes[4]], execution_type=ExecutionType.SEQUENTIAL, order=3),
        ExecutionGroup(nodes=[nodes[5]], execution_type=ExecutionType.SEQUENTIAL, order=4),
        ExecutionGroup(nodes=[nodes[6]], execution_type=ExecutionType.SEQUENTIAL, order=5),
    ]
    return nodes, edges, groups


def _dag_refinar_busca() -> tuple[list[DAGNode], list[DAGEdge], list[ExecutionGroup]]:
    nodes = [
        DAGNode(id="n1", agent_id="web_scraper", dependencies=[]),
        DAGNode(id="n2", agent_id="normalize", dependencies=["n1"]),
        DAGNode(id="n3", agent_id="compare_properties", dependencies=["n2"]),
    ]
    edges = [
        DAGEdge(from_node="n1", to_node="n2", edge_type=EdgeType.SEQUENTIAL),
        DAGEdge(from_node="n2", to_node="n3", edge_type=EdgeType.SEQUENTIAL),
    ]
    groups = [
        ExecutionGroup(nodes=[nodes[0]], execution_type=ExecutionType.SEQUENTIAL, order=0),
        ExecutionGroup(nodes=[nodes[1]], execution_type=ExecutionType.SEQUENTIAL, order=1),
        ExecutionGroup(nodes=[nodes[2]], execution_type=ExecutionType.SEQUENTIAL, order=2),
    ]
    return nodes, edges, groups


# ── Mapeamento intent → DAG builder ─────────────────────────

DAG_TEMPLATES = {
    "buscar_imoveis":  _dag_buscar_imoveis,
    "analisar_imovel": _dag_analisar_imovel,
    "investimento":    _dag_investimento,
    "refinar_busca":   _dag_refinar_busca,
}


# ── DAGResolver ──────────────────────────────────────────────

class DAGResolver:
    """
    Converte RoutingResult em ExecutionDAG.
    Suporta intents compostos via merge de DAGs com deduplicação de agentes.
    """

    def resolve(self, routing: RoutingResult) -> ExecutionDAG:
        """
        Resolve o DAG para o(s) intent(s) detectados.

        Args:
            routing: resultado do SemanticRouter

        Returns:
            ExecutionDAG pronto para o Orchestrator
        """
        primary = routing.primary_intent

        if routing.is_compound and routing.secondary_intent:
            return self._resolve_compound(primary, routing.secondary_intent)

        return self._resolve_single(primary)

    def _resolve_single(self, intent: str) -> ExecutionDAG:
        """Resolve DAG para um intent simples."""
        builder = DAG_TEMPLATES.get(intent)

        if builder is None:
            # Fallback: se intent desconhecido, usar buscar_imoveis como default
            builder = DAG_TEMPLATES["buscar_imoveis"]

        nodes, edges, groups = builder()

        return ExecutionDAG(
            nodes=nodes,
            edges=edges,
            execution_groups=groups,
            estimated_steps=len(groups),
            intent=intent,
        )

    def _resolve_compound(self, primary: str, secondary: str) -> ExecutionDAG:
        """
        Resolve DAG composto: merge de dois DAGs com deduplicação.
        Prioridade: o intent com maior confidence tem seus nós primeiro.
        """
        primary_dag = self._resolve_single(primary)
        secondary_dag = self._resolve_single(secondary)

        # Coletar agent_ids já presentes no DAG primário
        existing_agents = set(primary_dag.agent_ids)

        # Adicionar nós do DAG secundário que não existem no primário
        merged_nodes = list(primary_dag.nodes)
        extra_nodes = []

        for node in secondary_dag.nodes:
            if node.agent_id not in existing_agents:
                # Renumerar IDs para evitar conflito
                new_id = f"s{node.id}"
                new_node = DAGNode(
                    id=new_id,
                    agent_id=node.agent_id,
                    dependencies=[f"s{d}" if d != node.id else d for d in node.dependencies],
                )
                extra_nodes.append(new_node)
                existing_agents.add(node.agent_id)

        # Se existem nós extras, conectá-los ao final do DAG primário
        if extra_nodes:
            last_primary_node = primary_dag.nodes[-1]
            for extra in extra_nodes:
                if not extra.dependencies:
                    extra.dependencies = [last_primary_node.id]

            merged_nodes.extend(extra_nodes)

        # Recalcular edges
        merged_edges = list(primary_dag.edges)
        for extra in extra_nodes:
            for dep in extra.dependencies:
                merged_edges.append(
                    DAGEdge(from_node=dep, to_node=extra.id, edge_type=EdgeType.SEQUENTIAL)
                )

        # Grupos: manter os do primário + um grupo extra sequencial
        merged_groups = list(primary_dag.execution_groups)
        if extra_nodes:
            merged_groups.append(
                ExecutionGroup(
                    nodes=extra_nodes,
                    execution_type=ExecutionType.SEQUENTIAL,
                    order=len(merged_groups),
                )
            )

        return ExecutionDAG(
            nodes=merged_nodes,
            edges=merged_edges,
            execution_groups=merged_groups,
            estimated_steps=len(merged_groups),
            intent=f"{primary}+{secondary}",
        )
