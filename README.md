# IMOBILAY

**Consultor Inteligente de Investimentos Imobiliários**

O IMOBILAY é uma plataforma completa de consultoria imobiliária baseada em inteligência artificial. A proposta é entregar análises estruturadas e fundamentadas em dados — não texto livre gerado por IA — através de uma interface de chat premium, similar a um relatório da JLL com a fluidez de um produto consumer moderno.

---

## 📋 Visão Geral do Escopo

O projeto está dividido em **três grandes pilares**, cada um documentado em detalhe na pasta `context/`:

| Pilar | Documento | Descrição |
|---|---|---|
| **Frontend** | `imobilay_front.md` | Interface React + Vite com design de alto padrão |
| **Backend** | `imobilay_back.md` | Sistema multi-agente com pipeline de decisão automatizada |
| **Banco de Dados** | `baserelacional.md` | Schema PostgreSQL no Supabase com pgvector |

---

## 🎨 Frontend — Interface de Chat Premium

### Stack

- **React 18 + Vite + TypeScript**
- **Framer Motion** para todas as animações
- **Tailwind CSS v3** para estilização
- **Lucide React** para ícones (uso com parcimônia)
- **Fontes:** Cormorant Garamond (títulos) + DM Sans (corpo) — nenhum uso de Inter, Roboto ou system-ui

### Identidade Visual

O tom visual é de **consultoria de alto padrão**: confiança técnica sem frieza. A paleta principal gira em torno de:

- **Gold** (`#B8960C`) — accent principal, usado com extrema parcimônia
- **Navy** (`#0D1B2A`) — fundo das mensagens do usuário
- **Surface** (`#F9F8F6`) — nunca branco puro
- **Green/Coral** — indicadores positivos e negativos nos scores
- Sem gradients, sem box-shadow pesado

### Layout

A interface é composta por **Sidebar** (220px) + **Área de Chat Principal** (TopBar, mensagens e input):

#### Sidebar
- Logo "IMOBI" + "LAY" com destaque dourado
- Ações fixas: "Nova análise" e "Alertas" (com badge numérico)
- Histórico de conversas agrupado por período (Hoje / Ontem / Esta Semana / Meses), estilo Claude.ai
- Footer com perfil do usuário e popover de configurações

#### Área de Chat
- **TopBar** com título editável e pill de status animado ("Sistema online", "Analisando...")
- **Mensagens do usuário** em bubbles navy com border-radius assimétrico
- **Respostas do IMOBILAY** com:
  - **Pipeline Indicator** — chips horizontais mostrando as fases reais do processamento: `[Busca] › [Normalização] › [Precificação] › [ROI] › [Ranking]`
  - **Texto introdutório** contextualizando a análise
  - **PropertyAnalysisCard** — card principal com endereço, specs, preço pedido vs preço justo, ROI estimado e barras de score animadas (Localização, Preço vs Mercado, Liquidez)
  - **ConfidenceGate** — estado especial quando há dados insuficientes (nunca erro genérico)
- **Input de chat** com placeholder contextual que muda durante a análise

### Animações

Todas as animações usam easing personalizado (`[0.16, 1, 0.3, 1]`), nunca linear ou ease padrão. Destaques:
- Mensagens surgem com slide-up + fade-in
- Chips do pipeline em stagger com pulse no chip ativo
- Score bars animam de 0% ao valor com stagger de 80ms
- Sidebar ativa com `layoutId` para transição suave entre items

### Tipos TypeScript Principais

- `PropertyAnalysis` — dados completos de um imóvel (endereço, specs, pricing, ROI, scores)
- `Message` — mensagem de chat com análise opcional e fase do pipeline
- `UserProfile` — perfil com plano (free/pro/elite), contagem de análises e preferências

---

## 🧠 Backend — Sistema Multi-Agente

O backend é construído em **Python 3.11+** com tipagem estática obrigatória, dividido em **3 camadas** independentes:

### Camada 1 — Entrada e Roteamento Semântico

Responsável por receber a mensagem, classificar a intenção **sem LLM** (via embedding similarity) e resolver o grafo de execução (DAG).

| Componente | Função |
|---|---|
| `InputProcessor` | Normaliza a entrada do usuário e gera o `trace_id` (UUID propagado por todo o sistema) |
| `SemanticRouter` | Classifica intenção via `sentence-transformers` (modelo `all-MiniLM-L6-v2`). Suporta intents compostos quando dois scores superam 0.65 |
| `DAGResolver` | Converte intents em grafos de execução com nós PARALLEL, SEQUENTIAL e CONDITIONAL |
| `SharedContextStore` | Estado compartilhado imutável entre agentes, com sistema de patches e versionamento |

**Intents suportados:** `buscar_imoveis`, `analisar_imovel`, `investimento`, `refinar_busca`, e combinações compostas.

### Camada 2 — Orquestrador e Agentes Especializados

Executa o DAG, gerencia paralelismo com `asyncio.gather()`, resiliência e validação.

| Componente | Função |
|---|---|
| `Orchestrator` | Executa o DAG coordenando agentes em paralelo ou sequencial |
| `ResilienceManager` | Retry com backoff exponencial (100ms→400ms→1600ms), fallback por agente e circuit breaker (CLOSED→OPEN→HALF_OPEN) |
| `ConfidenceGate` | Valida completude do contexto antes de acionar o LLM |
| `ResponseVerbalizer` | **Único ponto de contato com LLM** (Gemini 2.5 Pro via Google GenAI SDK, temperature 0.3) |

**7 Agentes Trabalhadores:**

| Agente | Responsabilidade |
|---|---|
| `WebScraperAgent` | Busca imóveis em múltiplas fontes (ZAP, VivaReal, OLX) com `aiohttp`, timeout de 5s por fonte |
| `NormalizeAgent` | Padroniza campos, remove duplicatas, converte moeda/unidades |
| `LocationInsightsAgent` | Enriquece com score de bairro, segurança, liquidez e infraestrutura (geocoding + IBGE + OSM) |
| `ValuationAgent` | Calcula preço justo por m² baseado em comparáveis e classifica: "barato" / "justo" / "caro" |
| `InvestmentAnalysisAgent` | Calcula aluguel estimado, ROI mensal, payback em anos e potencial de valorização |
| `OpportunityDetectionAgent` | Identifica oportunidades (desvio < -8% AND liquidez ≥ média AND location ≥ 6.5) |
| `ComparePropertiesAgent` | Gera ranking final: preço (30%) + localização (25%) + investimento (25%) + oportunidade (20%) |

Todos os agentes seguem um contrato base (`BaseAgent`) com `execute()` e `validate_input()`, e declaram um `fallback_value` para garantir que o sistema **nunca pare** por falha de um único agente.

### Camada 3 — Aprendizado e Observabilidade

Retroalimenta o sistema com dados de uso real.

| Componente | Função |
|---|---|
| `FeedbackCollector` | Captura sinais explícitos (rating 1-5) e implícitos (refinamento, aceitação, abandono) |
| `MemoryManager` | Três tipos de memória: sessão (TTL: sessão), usuário (TTL: 90 dias), cache de resultados (TTL: 15min a 24h) |
| `ObservabilityLayer` | Métricas por execução (latência, fallback rate, confidence) com alertas automáticos |
| `RouterFeedbackLoop` | Recalcula pesos dos intents a cada 100 execuções com base em precisão e satisfação |

---

## 🗄️ Banco de Dados — Supabase (PostgreSQL)

### Tecnologia

- **Supabase** (PostgreSQL 15 gerenciado)
- **pgvector** para embeddings do SemanticRouter
- **Redis/Upstash** para cache temporário e estado do circuit breaker

### Tabelas Principais

| Tabela | Propósito |
|---|---|
| `user_profiles` | Extensão do auth.users com dados de produto (nome, plano, contagem de análises) |
| `investor_profiles` | Memória de longo prazo do investidor (risco, horizonte, capital, áreas preferidas) |
| `sessions` | Cada conversa com o IMOBILAY |
| `messages` | Cada turno de conversa com link ao trace de execução |
| `execution_traces` | Rastreabilidade completa do pipeline (intent, confidence, latência, agentes) |
| `feedback_records` | Sinais explícitos e implícitos de qualidade |
| `saved_properties` | Imóveis salvos como snapshot JSONB imutável |
| `intent_embeddings` | Vetores do SemanticRouter com índice HNSW para busca por similaridade |

### Segurança

- **Row Level Security (RLS)** ativado para todas as tabelas de usuário
- **Dois clientes separados:**
  - `system_client` (service_role) — usado pelos agentes do pipeline, bypassa RLS
  - `user_client` (anon + JWT) — usado pelo frontend, respeita RLS
- **Repository Pattern** — nenhum componente acessa o banco diretamente

### Regras Fundamentais

1. O `ContextStore` **nunca** é persistido durante a execução — vive em memória Python
2. Apenas o `ExecutionTrace` final é salvo no banco
3. Todo acesso ao banco passa por repositórios (`UserRepository`, `SessionRepository`, etc.)
4. `AsyncClient` obrigatório em todo o sistema para manter o paralelismo do orquestrador
5. IDs são `UUID` nos dataclasses, convertidos para `str` apenas na inserção

---

## 📁 Estrutura de Arquivos

```
imobilay/
├── context/                         ← Documentação de escopo
│   ├── imobilay_front.md            ← Especificação do frontend
│   ├── imobilay_back.md             ← Especificação do backend
│   └── baserelacional.md            ← Schema e integração com banco
│
├── src/                             ← Frontend (React + Vite)
│   ├── types/index.ts
│   ├── components/
│   │   ├── layout/                  ← Sidebar, TopBar
│   │   ├── chat/                    ← MessageList, ChatInput, PipelineIndicator
│   │   └── analysis/               ← PropertyAnalysisCard, ScoreBar, ConfidenceGate
│   ├── hooks/                       ← useChat, usePipeline
│   ├── data/mock.ts
│   └── styles/globals.css
│
├── layer_1_input/                   ← Camada 1: Entrada e Roteamento
│   ├── input_processor.py
│   ├── semantic_router.py
│   ├── dag_resolver.py
│   └── context_store.py
│
├── layer_2_orchestrator/            ← Camada 2: Orquestração e Agentes
│   ├── orchestrator.py
│   ├── resilience_manager.py
│   ├── confidence_gate.py
│   ├── response_verbalizer.py
│   └── agents/                      ← 7 agentes especializados
│
├── layer_3_learning/                ← Camada 3: Aprendizado e Observabilidade
│   ├── feedback_collector.py
│   ├── memory_manager.py
│   ├── observability_layer.py
│   └── router_feedback_loop.py
│
├── models/                          ← Tipos compartilhados (Pydantic/dataclasses)
│
├── database/                        ← Camada de dados
│   ├── client.py                    ← Clientes Supabase (system + user)
│   ├── migrations/001_initial.sql
│   └── repositories/               ← Repository Pattern
│
├── tests/                           ← Testes unitários (pytest)
├── main.py                          ← Entry point do backend
└── requirements.txt
```

---

## 🔧 Dependências Principais

### Backend (Python)

```
google-genai>=1.0.0            # LLM (Gemini) — apenas no ResponseVerbalizer
sentence-transformers>=2.7.0  # Embeddings para o SemanticRouter
aiohttp>=3.9.0             # Requests assíncronos no WebScraperAgent
pydantic>=2.7.0            # Tipagem e validação de dados
redis>=5.0.0               # Cache e estado do circuit breaker
supabase>=2.10.0           # Cliente Supabase async
structlog>=24.0.0          # Observabilidade estruturada
pytest>=8.0.0              # Testes unitários
pytest-asyncio>=0.23.0     # Testes assíncronos
```

### Frontend (Node.js)

```
react 18 + vite + typescript
framer-motion
tailwindcss v3
lucide-react
@fontsource/cormorant-garamond
@fontsource/dm-sans
```

---

## ✅ Critérios de Aceite

- [ ] Pipeline completo executa de ponta a ponta com `python main.py "quero um apartamento de 2 quartos em Goiânia para investir"`
- [ ] Nenhum LLM é chamado fora do `ResponseVerbalizer`
- [ ] Circuit breaker muda de estado corretamente após 5 falhas consecutivas
- [ ] DAG composto executa `location_insights` e `valuation` em paralelo
- [ ] `ConfidenceGate` bloqueia o LLM e retorna `LimitationResponse` quando `properties` está vazio
- [ ] `ContextStore` mantém histórico completo de patches (imutável, não sobrescreve)
- [ ] Todos os testes unitários passam com `pytest tests/`
- [ ] `ObservabilityLayer` emite WARNING quando latência > 8000ms
- [ ] Frontend com animações Framer Motion funcionais em todos os componentes
- [ ] Interface responsiva com sidebar em overlay no mobile

---

## 🚀 Ordem de Implementação Recomendada

1. `models/` — todos os dataclasses/pydantic models (fundação)
2. `context_store.py` — estado compartilhado com patch imutável
3. `semantic_router.py` — com embedding mock inicial
4. `dag_resolver.py` — DAGs fixos por intent
5. `base_agent.py` + agentes simples (`normalize`, `compare_properties`)
6. `resilience_manager.py` — testar com agente que falha intencionalmente
7. `orchestrator.py` — ligar tudo com asyncio
8. `confidence_gate.py`
9. `response_verbalizer.py` — integração com Google GenAI SDK
10. Agentes restantes (web_scraper, location_insights, valuation, investment, opportunity)
11. `layer_3_learning/` inteiro
12. `main.py` + testes de integração
13. Frontend completo com Vite + React

---

> **Nota:** O arquivo `context/escopo.md` está atualmente vazio. Toda a especificação do escopo do projeto está distribuída entre os três documentos de contexto: `imobilay_front.md`, `imobilay_back.md` e `baserelacional.md`.
