import pytest
from layer_1_input.dag_resolver import DAGResolver
from models.routing import RoutingResult

def test_dag_resolver_investment():
    resolver = DAGResolver()
    routing = RoutingResult(
        message="investimento imobiliario",
        primary_intent="investimento",
        confidence=0.9
    )
    dag = resolver.resolve(routing)
    
    assert dag.intent == "investimento"
    assert "web_scraper" in [n.agent_id for n in dag.nodes]
    assert "investment_analysis" in [n.agent_id for n in dag.nodes]

def test_dag_resolver_fallback():
    resolver = DAGResolver()
    routing = RoutingResult(
        message="bom dia",
        primary_intent="greeting",
        confidence=0.9
    )
    dag = resolver.resolve(routing)
    
    # Defaults to empty dag for smalltalk/greeting
    assert len(dag.nodes) == 0
    assert len(dag.execution_groups) == 0
