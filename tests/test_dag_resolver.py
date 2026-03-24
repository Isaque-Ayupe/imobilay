import pytest
from layer_1_input.dag_resolver import DAGResolver
from models.routing import RoutingResult

def test_dag_resolver_investment():
    resolver = DAGResolver()
    routing = RoutingResult(
        message="investimento imobiliario",
        primary_intent="investment_analysis",
        confidence=0.9
    )
    dag = resolver.resolve(routing)
    
    assert dag.intent == "investment_analysis"
    assert "web_scraper" in dag.nodes
    assert "investment_analysis" in dag.nodes

def test_dag_resolver_fallback():
    resolver = DAGResolver()
    routing = RoutingResult(
        message="bom dia",
        primary_intent="greeting",
        confidence=0.9
    )
    dag = resolver.resolve(routing)
    
    assert len(dag.nodes) == 0
    assert "valuation" not in dag.nodes
