---
name: project-context
description: Arquitetura e padrões do IMOBILAY — consultor inteligente de investimentos imobiliários com pipeline de 3 camadas. LLMs apenas verbalizam; toda lógica analítica é determinística.
user-invocable: false
---

# IMOBILAY — Contexto do Projeto

## Visão Geral

IMOBILAY é um consultor inteligente de investimentos imobiliários. Usuários enviam queries em linguagem natural (ex: "quero kitnet perto da berrini") e o sistema busca, avalia, pontua e rankeia propriedades usando agentes especializados. Regra fundamental: **LLMs apenas verbalizam respostas; toda lógica analítica é Python determinístico.**

## Tech Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.14, FastAPI, Uvicorn |
| ML | sentence-transformers (embeddings locais) |
| LLM | Google Gemini (verbalização) |
| Banco | Supabase (PostgreSQL) + Redis (cache) |
| Frontend | React 19 + TypeScript + Vite + TailwindCSS 4 |
| Testes | pytest + pytest-asyncio |

## Arquitetura em 3 Camadas

### Layer 1: Input & Routing (`layer_1_input/`)

- `InputProcessor` — sanitização e extração de metadata
- `SemanticRouter` — classificação de intenção via embeddings locais (não LLM)
- `DAGResolver` — constrói grafos de execução baseados no routing
- `ContextStore` — inicializa o contexto da execução

### Layer 2: Orchestration (`layer_2_orchestrator/`)

- `Orchestrator` — executa agentes em paralelo via asyncio
- 7 agentes especialistas:
  - `WebScraperAgent` — coleta dados de propriedades
  - `NormalizeAgent` — normaliza dados coletados
  - `LocationInsightsAgent` — análise de localização
  - `ValuationAgent` — avaliação de preço/valor
  - `InvestmentAnalysisAgent` — análise de investimento
  - `OpportunityDetectionAgent` — detecção de oportunidades
  - `ComparePropertiesAgent` — comparação entre propriedades
- `ConfidenceGate` — valida qualidade dos resultados
- `ResponseVerbalizer` — LLM verbaliza a resposta final

### Layer 3: Learning (`layer_3_learning/`)

- `MemoryManager` — memória de sessão + longa duração (+ Redis)
- `ObservabilityLayer` — métricas, latência, feedback

## Componentes Principais

- **Models** (`models/`): `ContextStore`, `ContextPatch`, `UserProfile` — Pydantic
- **Database** (`database/`): cliente Supabase + repositórios
- **API** (`api.py`): endpoints `/api/chat`, `/api/sessions`, `/api/health`
- **Pipeline** (`main.py`):入口 E2E — pode ser CLI ou via API

## Padrões Importantes

1. **BaseAgent** (`layer_2_orchestrator/agents/base_agent.py`): contrato ABC para todos os agentes. Cada agente implementa `execute(context) -> ContextPatch` e opcionalmente `validate_input()`.
2. **Patch-based communication**: agentes não modificam contexto diretamente — retornam `ContextPatch` que o orchestrator aplica.
3. **DAG execution**: grupos de agentes executam em paralelo; grupos subsequentes dependem dos anteriores.
4. **Fallback resilience**: cada agente declara `fallback_value`; o `ResilienceManager` aplica fallbacks automaticamente.
5. **Circuit breaker**: a camada de resiliência previne cascateamento de falhas.

## Arquivos de referência

- Ponto de entrada: `main.py`, `api.py`
- Config: `.claude/settings.local.json`
- Env: `.env` (gerenciado com `python-dotenv`)
- Migrations: `supabase/migrations/`
