---
name: add-agent
description: Guia passo a passo para adicionar novos agentes especialistas ao orchestrator do IMOBILAY.
disable-model-invocation: true
allowed-tools: Read Bash Edit Glob
---

# Adicionar Novo Agente Especialista

## Contexto

Cada agente especialista é responsável por uma fatia da análise imobiliária. Todos herdam de `BaseAgent` e são executados pelo `Orchestrator` via DAG em paralelo. Lembre-se: **agentes não usam LLMs** — toda lógica é determinística.

## Contrato do BaseAgent

Arquivo: `layer_2_orchestrator/agents/base_agent.py`

Todo agente implementa:

```python
class MeuAgente(BaseAgent):
    agent_id = "meu_agente"          # ID único (snake_case)
    fallback_value = None            # Valor em caso de falha

    async def execute(self, context: ContextStore) -> ContextPatch:
        # Lê de context, computa, retorna ContextPatch
        ...

    @property
    def _output_field(self) -> str:
        return "meu_campo_no_context"  # Campo do ContextStore que escreve
```

## Passo a passo

### 1. Criar arquivo do agente

```
layer_2_orchestrator/agents/meu_agente.py
```

Seguir o padrão dos agentes existentes em `layer_2_orchestrator/agents/`:

- `web_scraper_agent.py`
- `normalize_agent.py`
- `location_insights_agent.py`
- `valuation_agent.py`
- `investment_analysis_agent.py`
- `opportunity_detection_agent.py`
- `compare_properties_agent.py`

### 2. Registrar no __init__

Adicionar o import em `layer_2_orchestrator/agents/__init__.py`.

### 3. Registrar no DAG

Em `layer_1_input/dag_resolver.py`, adicionar o agente ao grupo correto do DAG:

- **Grupo 1 (coleta)**: agentes que buscam dados brutos
- **Grupo 2 (processamento)**: agentes que normalizam/analisam
- **Grupo 3 (conclusão)**: agentes que sintetizam resultados

Agentes no mesmo grupo rodam em paralelo. Grupos rodam sequencialmente.

### 4. Adicionar campo ao ContextStore

Se o agente escreve um campo novo, adicionar em `models/context.py`:

```python
class ContextPatch(BaseModel):
    meu_campo: Optional[Any] = None
```

### 5. Adicionar teste

Criar `tests/test_meu_agente.py` seguindo padrões dos testes existentes (pytest + pytest-asyncio).

## Checklist

- [ ] Herда de `BaseAgent`
- [ ] `agent_id` único em snake_case
- [ ] `execute(context) -> ContextPatch` implementado
- [ ] `_output_field` retorna nome do campo no ContextStore
- [ ] `fallback_value` definido
- [ ] Registrado no `__init__.py`
- [ ] Registrado no DAG resolver
- [ ] Campo adicionado no ContextStore/ContextPatch
- [ ] Teste unitário criado
- [ ] Não usa LLM (lógica 100% determinística)
