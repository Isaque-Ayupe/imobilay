# Directive 02 — Models (Tipos Compartilhados)

## Objetivo
Implementar todos os Pydantic models e dataclasses que são a fundação de tipos do sistema inteiro. Nenhum outro módulo deve ser implementado antes destes models estarem prontos.

## Inputs
- Especificação completa em `context/imobilay_back.md` (seção "TIPOS TYPESCRIPT" adaptada para Python)
- Especificação de banco em `context/baserelacional.md` (tabelas → dataclasses)

## Scripts/Tools
- Nenhum script de execução necessário — implementação direta em código

## Estrutura de Arquivos

```
models/
├── __init__.py          ← re-exporta tudo
├── property.py          ← Property, RawProperty, ValuationResult, InvestmentResult
├── context.py           ← ContextStore, ContextPatch, AgentError, CompletenessReport
├── routing.py           ← RoutingResult, ExecutionDAG, DAGNode, DAGEdge, ExecutionGroup
└── feedback.py          ← FeedbackRecord, ExecutionTrace, ExecutionMetrics
```

## Especificação por Arquivo

### `models/property.py`
```python
# Tipos a implementar:
RawProperty          # dados brutos do scraper
Property             # imóvel normalizado com location_insights
ValuationResult      # preço justo, desvio, classificação
InvestmentResult     # ROI, payback, potencial
Opportunity          # oportunidade detectada com score composto
RankingResult        # ranking final com melhor_opcao e justificativa
```

Campos obrigatórios de `Property`:
- `id: str` (UUID)
- `address: str`, `neighborhood: str`, `city: str`
- `rooms: int`, `area: float`, `parking: int`, `floor: int | None`
- `price: float`, `price_per_sqm: float`
- `property_type: str` (apartamento, studio, cobertura, etc.)
- `source: str` (ZAP, VivaReal, OLX)
- `location_insights: LocationInsights | None` (score, segurança, liquidez, infra)

### `models/context.py`
```python
# Tipos a implementar:
ContextPatch         # agent_id, field, value, timestamp, version
AgentError           # agent_id, error_type, message, severity("WARNING"|"ERROR"|"CRITICAL")
CompletenessReport   # campos faltantes, cobertura, recomendação
ContextStore         # estado central imutável com patches
  # Campos: trace_id, input, properties, analysis, user, errors, patches
  # Métodos: apply_patch(), get_snapshot(), validate_completeness()
```

> **REGRA:** `ContextStore` usa sistema de patches imutáveis. `apply_patch()` retorna uma NOVA instância, nunca muta a existente.

### `models/routing.py`
```python
# Tipos a implementar:
RoutingResult        # primary_intent, secondary_intent, confidence, is_compound, raw_scores
DAGNode              # id, agent_id, dependencies: list[str]
DAGEdge              # from_node, to_node, edge_type(SEQUENTIAL|PARALLEL|CONDITIONAL)
ExecutionGroup       # nodes: list[DAGNode], execution_type
ExecutionDAG         # nodes, edges, execution_groups, estimated_steps
```

### `models/feedback.py`
```python
# Tipos a implementar:
FeedbackRecord       # trace_id, session_id, user_id, ratings, signals, agents
AgentExecutionRecord # agent_id, status, duration_ms, error, patch_applied
ExecutionMetrics     # latências, taxas, scores
ExecutionTrace       # trace completo com DAG, records, patches, gate, feedback, metrics
```

## Outputs
- 4 arquivos Python com todos os types/models
- `__init__.py` re-exportando tudo para fácil importação: `from models import Property, ContextStore`
- Todos os models com tipagem estática completa
- Validação via Pydantic v2 (`model_validator`, `field_validator` onde necessário)

## Edge Cases
- `ContextStore.apply_patch()` deve lidar com campos nested (ex: `analysis.valuation`)
- `Property.price` e `Property.area` devem ser > 0 (validação Pydantic)
- `AgentError.severity` é enum restrito: WARNING, ERROR, CRITICAL
- `RankingResult.best_option` pode ser `None` se nenhum imóvel atender os critérios mínimos
