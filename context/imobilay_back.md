# IMOBILAY — Prompt de Engenharia para Gemini 2.5 Pro

> **Contexto:** Você é um engenheiro sênior especializado em sistemas multi-agente com foco em decisão automatizada. Sua tarefa é implementar o sistema IMOBILAY — um consultor imobiliário inteligente baseado em agentes especializados. O sistema é dividido em três camadas independentes e bem definidas. Implemente cada camada de forma modular, com interfaces claras entre elas.

---

## REGRAS GLOBAIS DE IMPLEMENTAÇÃO

- Linguagem: **Python 3.11+**
- Tipagem estática obrigatória em todas as funções (`typing`, `dataclasses` ou `pydantic`)
- Cada camada deve ser um módulo Python separado (`layer_1_input/`, `layer_2_orchestrator/`, `layer_3_learning/`)
- Nenhum LLM deve ser chamado fora da etapa de verbalização final
- Todo estado compartilhado é imutável por padrão — agentes escrevem via `patch`, nunca sobrescrevem diretamente
- Cada execução gera um `trace_id` único e tem seu ciclo completo rastreado
- Testes unitários para cada componente com `pytest`

---

## CAMADA 1 — ENTRADA E ROTEAMENTO SEMÂNTICO

### Objetivo
Receber a mensagem do usuário, classificar a intenção por similaridade de embedding (nunca via LLM), e resolver o grafo de execução (DAG) antes de acionar qualquer agente.

### Componentes a implementar

#### 1.1 `InputProcessor`
```
Responsabilidade: normalizar a entrada do usuário.

Entrada:
  - raw_message: str
  - session_id: str
  - user_profile: UserProfile | None

Saída:
  - ProcessedInput:
      message: str
      session_id: str
      user_profile: UserProfile
      timestamp: datetime
      trace_id: str  # UUID gerado aqui, propagado por todo o sistema
```

#### 1.2 `SemanticRouter`
```
Responsabilidade: classificar a intenção por embedding similarity. NÃO usar LLM.

Estratégia:
  - Usar sentence-transformers (modelo: all-MiniLM-L6-v2) para gerar embeddings
  - Comparar contra embeddings pré-computados de exemplos por intent
  - Retornar score de confiança (0.0 a 1.0)
  - Suportar intents compostos: se dois scores > 0.65 simultaneamente, gerar intent composto

Intents suportados:
  - buscar_imoveis
  - analisar_imovel
  - investimento
  - refinar_busca
  - Compostos: buscar_imoveis+investimento | analisar_imovel+investimento

Saída:
  - RoutingResult:
      primary_intent: str
      secondary_intent: str | None
      confidence: float
      is_compound: bool
      raw_scores: dict[str, float]
```

#### 1.3 `DAGResolver`
```
Responsabilidade: converter o(s) intent(s) em um grafo de execução com dependências explícitas.

Regras de construção do DAG:
  - Nodes sem dependências entre si → marcados como PARALLEL
  - Nodes cujo input depende do output de outro → marcados como SEQUENTIAL
  - Nodes ativados apenas se resultado anterior atende condição → marcados como CONDITIONAL

Mapeamento de intents para DAGs:

  buscar_imoveis:
    [web_scraper] → [normalize] → [location_insights, valuation] (parallel) → [compare_properties]

  analisar_imovel:
    [location_insights] → [valuation] → [investment_analysis]

  investimento:
    [web_scraper] → [normalize] → [location_insights, valuation] (parallel) → [investment_analysis] → [opportunity_detection] → [compare_properties]

  refinar_busca:
    [user_memory] → [web_scraper] → [normalize] → [compare_properties]

  Composto (buscar+investimento):
    Merge dos dois DAGs com deduplicação de nodes e resolução de conflitos de ordem

Saída:
  - ExecutionDAG:
      nodes: list[DAGNode]
      edges: list[DAGEdge]
      execution_groups: list[ExecutionGroup]  # grupos que podem rodar em paralelo
      estimated_steps: int
```

#### 1.4 `SharedContextStore`
```
Responsabilidade: estado compartilhado entre todos os agentes. Imutável por padrão.

Estrutura base:
  - ContextStore:
      trace_id: str
      created_at: datetime
      version: int
      input: ProcessedInput
      properties: list[Property]
      analysis:
        valuation: list[ValuationResult]
        investment: list[InvestmentResult]
        ranking: RankingResult | None
        opportunities: list[Opportunity]
      user: UserProfile
      errors: list[AgentError]
      patches: list[ContextPatch]  # histórico imutável de todas as escritas

Operações:
  - apply_patch(agent_id: str, field: str, value: Any) → ContextStore  # retorna nova versão
  - get_snapshot(version: int) → ContextStore  # acesso a versões anteriores
  - validate_completeness() → CompletenessReport  # usado pelo confidence gate
```

---

## CAMADA 2 — ORQUESTRADOR E AGENTES ESPECIALIZADOS

### Objetivo
Executar o DAG construído na Camada 1, gerenciar paralelismo, resiliência e validação antes de acionar o LLM.

### Componentes a implementar

#### 2.1 `Orchestrator` (Supervisor Agent)
```
Responsabilidade: executar o DAG, coordenar agentes, gerenciar estado.

Lógica de execução:
  1. Receber DAG + ContextStore da Camada 1
  2. Para cada ExecutionGroup no DAG:
     a. Se PARALLEL → executar agents com asyncio.gather()
     b. Se SEQUENTIAL → executar em ordem, passando output como input do próximo
     c. Se CONDITIONAL → avaliar predicado antes de acionar o agent
  3. Após cada agent, aplicar patch no ContextStore
  4. Em caso de falha, acionar ResilienceManager
  5. Ao final, passar contexto para o ConfidenceGate

Interface do Orchestrator:
  - async execute(dag: ExecutionDAG, context: ContextStore) → OrchestratorResult
  - OrchestratorResult:
      context: ContextStore
      execution_trace: list[AgentExecutionRecord]
      total_duration_ms: int
      agents_failed: list[str]
      agents_skipped: list[str]
```

#### 2.2 `ResilienceManager`
```
Responsabilidade: retry, fallback e circuit breaker por agente.

Retry:
  - Máximo 3 tentativas por agente
  - Backoff exponencial: 100ms, 400ms, 1600ms
  - Retry apenas em erros transitórios (timeout, HTTP 5xx)
  - Erros de dados (HTTP 4xx, parse error) → fallback imediato

Fallback:
  - Cada agente declara seu `fallback_value` (dados parciais aceitáveis)
  - Em caso de falha definitiva, preencher com fallback_value + registrar AgentError no context
  - Sistema nunca para por falha de um único agente

Circuit Breaker (por agente):
  - Estado: CLOSED | OPEN | HALF_OPEN
  - Abre após 5 falhas consecutivas em janela de 60s
  - Permanece aberto por 30s, então vai para HALF_OPEN
  - Fecha ao primeiro sucesso em HALF_OPEN
  - Em estado OPEN: retornar fallback_value imediatamente sem tentar

Interface:
  - async call_with_resilience(agent_fn, agent_id, *args) → AgentResult
  - get_circuit_state(agent_id: str) → CircuitState
  - get_health_report() → dict[str, AgentHealthStats]
```

#### 2.3 Agentes Especializados (Workers)

Cada agente segue o contrato:
```python
class BaseAgent(ABC):
    agent_id: str
    fallback_value: Any

    @abstractmethod
    async def execute(self, context: ContextStore) -> ContextPatch:
        """Lê do context, retorna patch com resultado."""

    @abstractmethod
    def validate_input(self, context: ContextStore) -> bool:
        """Verifica se o context tem o mínimo necessário para executar."""
```

**Agente `WebScraperAgent`**
```
- Buscar imóveis em múltiplas fontes (ZAP, VivaReal, OLX como exemplos)
- Executar requests em paralelo com aiohttp
- Timeout por fonte: 5s
- Retornar lista de RawProperty[]
- Fallback: retornar lista vazia com AgentError descritivo
- Patch: context.properties (raw)
```

**Agente `NormalizeAgent`**
```
- Receber context.properties (raw)
- Padronizar campos: preco, area, quartos, bairro, tipo
- Remover duplicatas por (endereço + preco + area)
- Converter moeda, unidades e formatos
- Patch: context.properties (normalizado, substitui raw)
```

**Agente `LocationInsightsAgent`**
```
- Para cada imóvel em context.properties
- Enriquecer com: bairro_score, seguranca_index, liquidez_estimada, infraestrutura_proxima
- Usar API de geocoding + dados públicos (IBGE, OSM)
- Fallback por imóvel: manter sem enriquecimento, sinalizar campo como null
- Patch: adicionar location_insights em cada Property
```

**Agente `ValuationAgent`**
```
- Para cada imóvel em context.properties
- Calcular preco_justo por m² baseado em comparáveis do mesmo bairro
- Calcular desvio_percentual em relação ao preço anunciado
- Classificar: "barato" (desvio < -10%), "justo" (-10% a +10%), "caro" (> +10%)
- Patch: context.analysis.valuation[]
```

**Agente `InvestmentAnalysisAgent`**
```
- Para cada imóvel em context.analysis.valuation
- Calcular:
    aluguel_estimado: float  # baseado em % do valor de mercado por tipo/bairro
    roi_mensal: float        # aluguel_estimado / preco_imovel
    payback_anos: float      # preco_imovel / (aluguel_estimado * 12)
    potencial_valorizacao: "baixo" | "medio" | "alto"  # baseado em liquidez + infraestrutura
- Patch: context.analysis.investment[]
```

**Agente `OpportunityDetectionAgent`**
```
- Condições para classificar como oportunidade:
    desvio_percentual < -8%
    AND liquidez_estimada >= "media"
    AND location_score >= 6.5
- Ranquear oportunidades por score composto: 0.4*desvio + 0.3*liquidez + 0.3*location
- Patch: context.analysis.opportunities[]
```

**Agente `ComparePropertiesAgent`**
```
- Gerar ranking final dos imóveis com score ponderado:
    preco (30%) + localizacao (25%) + investimento (25%) + oportunidade (20%)
- Identificar melhor_opcao: id do imóvel com maior score
- Gerar justificativa estruturada (campos, não texto livre — o LLM gera o texto)
- Patch: context.analysis.ranking
```

#### 2.4 `ConfidenceGate`
```
Responsabilidade: validar completude do context antes de acionar o LLM.

Regras de validação:
  - Mínimo de imóveis: >= 1 após scraping
  - Cobertura de valuation: >= 80% dos imóveis têm preco_justo calculado
  - Ranking presente: context.analysis.ranking is not None
  - Sem erros críticos: nenhum AgentError com severity="CRITICAL"

Saída:
  - GateResult:
      passed: bool
      score: float  # 0.0 a 1.0
      missing_fields: list[str]
      recommendation: "proceed" | "proceed_with_warning" | "return_limitation"

Se return_limitation:
  - Gerar LimitationResponse estruturada explicando o que faltou
  - Não acionar LLM
```

#### 2.5 `ResponseVerbalizer` (único ponto de contato com LLM)
```
Responsabilidade: transformar o ContextStore validado em linguagem natural.

Regras obrigatórias:
  - NUNCA inventar dados — apenas verbalizar o que está no context
  - NUNCA acessar campos com valor None sem tratar
  - Sempre citar o imóvel pelo ID + endereço ao fazer recomendações
  - Tom: consultor imobiliário sênior — direto, fundamentado, sem exageros

Prompt template a ser construído dinamicamente com dados do context:
  - Incluir: properties resumidas, ranking, melhor_opcao, justificativa, oportunidades
  - Excluir: campos nulos, erros internos, metadados de trace

Modelo a usar: gemini-2.5-pro via Google GenAI SDK
Max tokens: 1500
Temperature: 0.3  # respostas consistentes e factuais
```

---

## CAMADA 3 — APRENDIZADO E OBSERVABILIDADE

### Objetivo
Coletar feedback, manter memória por usuário e sessão, cachear resultados de tools, e retroalimentar o roteador semântico com dados de uso real.

### Componentes a implementar

#### 3.1 `FeedbackCollector`
```
Responsabilidade: capturar sinais de qualidade da resposta.

Feedback explícito:
  - rating: int (1-5) fornecido pelo usuário
  - comentario: str | None

Feedback implícito (inferir das ações seguintes):
  - refinamento: usuário fez follow-up pedindo ajuste → qualidade = "needs_improvement"
  - aceitação: usuário agiu sobre recomendação → qualidade = "good"
  - abandono: sem resposta após 30s → qualidade = "uncertain"

Saída:
  - FeedbackRecord:
      trace_id: str
      session_id: str
      user_id: str
      explicit_rating: int | None
      implicit_signal: str
      intent_original: str
      agents_used: list[str]
      agents_failed: list[str]
      total_duration_ms: int
      timestamp: datetime
```

#### 3.2 `MemoryManager`
```
Três tipos de memória com TTLs distintos:

SessionMemory (TTL: duração da sessão):
  - preferencias_reveladas: dict  # filtros que o usuário aplicou na conversa
  - refinamentos_pedidos: list[str]  # o que o usuário pediu para ajustar
  - imoveis_descartados: list[str]  # IDs rejeitados explicitamente

UserMemory (TTL: 90 dias, persistido em banco):
  - historico_buscas: list[SearchRecord]
  - perfil_investidor: InvestorProfile  # risco, horizonte, capital estimado
  - bairros_preferidos: list[str]
  - faixas_preco: PriceRange
  - tipo_imovel_preferido: list[str]

ResultCache (TTL: variável por tipo):
  - web_scraper results: TTL 15 minutos
  - location_insights: TTL 24 horas
  - valuation comparáveis: TTL 6 horas
  - Chave de cache: hash(intent + filtros_normalizados)

Interface:
  - get_session(session_id) → SessionMemory
  - get_user(user_id) → UserMemory
  - update_user(user_id, patch: UserMemoryPatch) → UserMemory
  - get_cached(cache_key: str) → CachedResult | None
  - set_cached(cache_key: str, value: Any, ttl_seconds: int) → None
```

#### 3.3 `ObservabilityLayer`
```
Responsabilidade: rastrear e emitir métricas de cada execução.

Métricas a coletar por execução (trace_id):
  - latencia_total_ms: int
  - latencia_por_agent: dict[str, int]
  - taxa_fallback_por_agent: dict[str, float]  # acumulado por janela de 1h
  - confidence_gate_score: float
  - intent_detectado: str
  - intent_confidence: float
  - properties_encontradas: int
  - properties_com_valuation: int
  - oportunidades_detectadas: int

Alertas automáticos (logar como WARNING):
  - latencia_total_ms > 8000
  - taxa_fallback_por_agent[agent] > 0.3 em janela de 10 execuções
  - confidence_gate_score < 0.5 em mais de 20% das execuções da última hora

Estrutura de trace completo:
  - ExecutionTrace:
      trace_id: str
      dag_resolved: ExecutionDAG
      agent_records: list[AgentExecutionRecord]
      context_patches: list[ContextPatch]
      gate_result: GateResult
      feedback: FeedbackRecord | None
      metrics: ExecutionMetrics
```

#### 3.4 `RouterFeedbackLoop`
```
Responsabilidade: usar dados de observabilidade para melhorar o roteador.

Lógica:
  - A cada 100 execuções, recalcular pesos dos intents por:
      precision = execucoes_sem_fallback_critico / total_execucoes_desse_intent
      satisfaction = media(explicit_rating) para esse intent
      peso_final = 0.6 * precision + 0.4 * satisfaction

  - Agentes com circuit_breaker em estado OPEN por mais de 5 minutos:
      → Sinalizar para o DAGResolver excluir esse agent do próximo DAG
      → Notificar via log ERROR com contexto completo

  - Se intent composto gera consistentemente mais satisfação que intent simples
    para o mesmo tipo de pergunta:
      → Atualizar threshold de confiança do SemanticRouter (de 0.65 para 0.60)

Interface:
  - async run_feedback_cycle() → RouterUpdateReport
  - get_agent_weights() → dict[str, float]
  - get_router_thresholds() → RouterThresholds
```

---

## ESTRUTURA DE ARQUIVOS ESPERADA

```
imobilay/
├── layer_1_input/
│   ├── __init__.py
│   ├── input_processor.py
│   ├── semantic_router.py
│   ├── dag_resolver.py
│   └── context_store.py
├── layer_2_orchestrator/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── resilience_manager.py
│   ├── confidence_gate.py
│   ├── response_verbalizer.py
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py
│       ├── web_scraper_agent.py
│       ├── normalize_agent.py
│       ├── location_insights_agent.py
│       ├── valuation_agent.py
│       ├── investment_analysis_agent.py
│       ├── opportunity_detection_agent.py
│       └── compare_properties_agent.py
├── layer_3_learning/
│   ├── __init__.py
│   ├── feedback_collector.py
│   ├── memory_manager.py
│   ├── observability_layer.py
│   └── router_feedback_loop.py
├── models/
│   ├── __init__.py
│   ├── property.py       # Property, RawProperty, ValuationResult, etc.
│   ├── context.py        # ContextStore, ContextPatch, AgentError
│   ├── routing.py        # RoutingResult, ExecutionDAG, DAGNode, DAGEdge
│   └── feedback.py       # FeedbackRecord, ExecutionTrace, ExecutionMetrics
├── tests/
│   ├── test_semantic_router.py
│   ├── test_dag_resolver.py
│   ├── test_orchestrator.py
│   ├── test_resilience_manager.py
│   ├── test_confidence_gate.py
│   └── test_memory_manager.py
├── main.py               # entry point: recebe mensagem, executa pipeline completo
└── requirements.txt
```

---

## ORDEM DE IMPLEMENTAÇÃO RECOMENDADA

1. `models/` — todos os dataclasses/pydantic models primeiro (fundação de tudo)
2. `context_store.py` — estado compartilhado com patch imutável
3. `semantic_router.py` — com embedding mock inicialmente, trocar por sentence-transformers depois
4. `dag_resolver.py` — DAGs fixos por intent, composto por merge
5. `base_agent.py` + dois agentes simples (`normalize`, `compare_properties`)
6. `resilience_manager.py` — testar com agente que falha intencionalmente
7. `orchestrator.py` — ligar tudo com asyncio
8. `confidence_gate.py`
9. `response_verbalizer.py` — integração com Google GenAI SDK
10. Agentes restantes (`web_scraper`, `location_insights`, `valuation`, `investment_analysis`, `opportunity_detection`)
11. `layer_3_learning/` inteiro
12. `main.py` + testes de integração

---

## DEPENDÊNCIAS PRINCIPAIS

```
google-genai>=1.0.0
sentence-transformers>=2.7.0
aiohttp>=3.9.0
pydantic>=2.7.0
asyncio
redis>=5.0.0         # para cache e circuit breaker state
structlog>=24.0.0    # para observabilidade estruturada
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## CRITÉRIOS DE ACEITE

- [ ] Pipeline completo executa de ponta a ponta com `python main.py "quero um apartamento de 2 quartos em Goiânia para investir"`
- [ ] Nenhum LLM é chamado fora do `ResponseVerbalizer`
- [ ] Circuit breaker muda de estado corretamente após 5 falhas consecutivas
- [ ] DAG composto `buscar_imoveis+investimento` executa `location_insights` e `valuation` em paralelo
- [ ] `ConfidenceGate` bloqueia o LLM e retorna `LimitationResponse` quando `properties` está vazio
- [ ] `ContextStore` mantém histórico completo de patches (não sobrescreve)
- [ ] Todos os testes unitários passam com `pytest tests/`
- [ ] `ObservabilityLayer` emite WARNING quando latência > 8000ms
