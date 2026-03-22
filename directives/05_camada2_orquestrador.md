# Directive 05 — Camada 2: Orquestrador e Agentes Especializados

## Objetivo
Implementar o núcleo de execução do IMOBILAY: o orquestrador que executa o DAG, o gerenciador de resiliência, o gate de confiança, o verbalizador (único ponto de LLM) e os 7 agentes especializados.

## Inputs
- Especificação em `context/imobilay_back.md` → seção "CAMADA 2"
- Models prontos (Directive 02)
- DAG do roteador (Directive 04)

## Scripts/Tools
- Nenhum script de execução separado — toda a lógica vive nos módulos Python

## Estrutura de Arquivos

```
layer_2_orchestrator/
├── __init__.py
├── orchestrator.py              ← Supervisor Agent
├── resilience_manager.py        ← Retry, fallback, circuit breaker
├── confidence_gate.py           ← Validação pré-LLM
├── response_verbalizer.py       ← Único ponto de LLM (Gemini)
└── agents/
    ├── __init__.py
    ├── base_agent.py            ← Contrato base ABC
    ├── web_scraper_agent.py     ← Busca em ZAP, VivaReal, OLX
    ├── normalize_agent.py       ← Padronização de dados
    ├── location_insights_agent.py  ← Enriquecimento geográfico
    ├── valuation_agent.py       ← Preço justo por comparáveis
    ├── investment_analysis_agent.py ← ROI, payback, valorização
    ├── opportunity_detection_agent.py ← Detecção de oportunidades
    └── compare_properties_agent.py   ← Ranking final
```

## Especificação por Componente

### 1. `Orchestrator`
```python
async execute(dag: ExecutionDAG, context: ContextStore) -> OrchestratorResult
```
- Para cada `ExecutionGroup` no DAG:
  - PARALLEL → `asyncio.gather()` nos agentes
  - SEQUENTIAL → execução em ordem, output → input do próximo
  - CONDITIONAL → avaliar predicado antes de acionar
- Após cada agente: `context.apply_patch(patch)`
- Em falha: acionar `ResilienceManager`
- Ao final: passar para `ConfidenceGate`

### 2. `ResilienceManager`
```python
async call_with_resilience(agent_fn, agent_id, *args) -> AgentResult
```
**Retry:** máx 3 tentativas, backoff 100ms → 400ms → 1600ms. Retry só em erros transitórios (timeout, HTTP 5xx).
**Fallback:** cada agente declara `fallback_value`. Em falha definitiva, usar fallback + registrar `AgentError`.
**Circuit Breaker (por agente):**
- CLOSED → OPEN após 5 falhas consecutivas em 60s
- OPEN (30s) → retorna fallback imediatamente
- HALF_OPEN → tenta 1 vez, sucesso = CLOSED, falha = OPEN

### 3. `ConfidenceGate`
```python
validate(context: ContextStore) -> GateResult
```
Regras:
- Mínimo 1 imóvel após scraping
- ≥ 80% dos imóveis com `preco_justo` calculado
- `context.analysis.ranking is not None`
- Nenhum `AgentError` com `severity="CRITICAL"`

Saída: `GateResult(passed, score, missing_fields, recommendation)`
- `"proceed"` — tudo OK
- `"proceed_with_warning"` — dados parciais, mas utilizáveis
- `"return_limitation"` — não acionar LLM, retornar `LimitationResponse`

### 4. `ResponseVerbalizer`
```python
async verbalize(context: ContextStore, gate: GateResult) -> str
```
- **ÚNICO ponto de contato com LLM** em TODO o sistema
- Modelo: Gemini 2.5 Pro via Google GenAI SDK
- Temperature: 0.3 (respostas consistentes)
- Max tokens: 1500
- NUNCA inventar dados — apenas verbalizar o que está no context
- Tom: consultor imobiliário sênior, direto, fundamentado

### 5. Agentes (todos seguem `BaseAgent`)
```python
class BaseAgent(ABC):
    agent_id: str
    fallback_value: Any

    async def execute(self, context: ContextStore) -> ContextPatch
    def validate_input(self, context: ContextStore) -> bool
```

| Agente | Input do Context | Output (Patch) | Fallback |
|---|---|---|---|
| `WebScraperAgent` | input.message (filtros) | `properties` (raw) | Lista vazia + error |
| `NormalizeAgent` | `properties` (raw) | `properties` (normalizado) | Manter raw |
| `LocationInsightsAgent` | `properties` | `location_insights` por imóvel | Null por imóvel |
| `ValuationAgent` | `properties` | `analysis.valuation[]` | Sem preço justo |
| `InvestmentAnalysisAgent` | `analysis.valuation` | `analysis.investment[]` | Sem ROI |
| `OpportunityDetectionAgent` | valuation + location | `analysis.opportunities[]` | Lista vazia |
| `ComparePropertiesAgent` | todos os analysis | `analysis.ranking` | Ranking simples por preço |

## Outputs
- 12 módulos Python funcionais
- Orchestrator executando DAGs com paralelismo real
- Circuit breaker testado com agente que falha intencionalmente
- Testes: `test_orchestrator.py`, `test_resilience_manager.py`, `test_confidence_gate.py`

## Edge Cases
- **WebScraperAgent:** timeout de 5s por fonte. Se TODAS as fontes falharem, circuit breaker abre → fallback: lista vazia + ConfidenceGate retorna `return_limitation`
- **Agente com circuit breaker OPEN por >5min:** `RouterFeedbackLoop` (Camada 3) deve excluir do próximo DAG
- **ContextStore vazio após pipeline:** nunca acontece — fallbacks garantem dados parciais
- **LLM timeout:** `ResponseVerbalizer` tem retry de 2 tentativas, depois retorna mensagem genérica estruturada (sem LLM)
- **Nunca chamar LLM fora do ResponseVerbalizer** — esta é regra absoluta
