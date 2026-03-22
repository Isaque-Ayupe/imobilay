# Directive 08 — Integração e Testes E2E

## Objetivo
Conectar todas as camadas no `main.py`, expor uma API para o frontend, implementar testes de integração e validar os critérios de aceite.

## Inputs
- Todas as 3 camadas backend funcionando (Directives 04, 05, 06)
- Frontend completo (Directive 07)
- Banco configurado (Directive 03)

## Scripts/Tools
- `execution/run_pipeline.py` — entry point para executar pipeline via CLI

## Estrutura de Arquivos

```
imobilay/
├── main.py                  ← Entry point: recebe mensagem, executa pipeline completo
├── api.py                   ← FastAPI/Flask expondo endpoints para o frontend
└── tests/
    ├── test_semantic_router.py
    ├── test_dag_resolver.py
    ├── test_orchestrator.py
    ├── test_resilience_manager.py
    ├── test_confidence_gate.py
    └── test_memory_manager.py
```

## Especificação

### `main.py`
```python
async def run_pipeline(message: str, user_id: str, session_id: str | None = None):
    # 1. InputProcessor → ProcessedInput (gera trace_id)
    # 2. MemoryManager → carregar UserMemory e SessionMemory
    # 3. SemanticRouter → RoutingResult (classificar intent)
    # 4. DAGResolver → ExecutionDAG (montar grafo)
    # 5. Orchestrator → executar DAG com agentes
    # 6. ConfidenceGate → validar contexto
    # 7. ResponseVerbalizer → gerar resposta (se gate passed)
    # 8. ObservabilityLayer → persistir trace
    # 9. FeedbackCollector → aguardar sinais implícitos
    # 10. Retornar resposta + analysis ao frontend
```

### `api.py` (endpoints)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/chat` | Enviar mensagem e receber resposta |
| GET | `/api/sessions` | Listar sessões do usuário |
| GET | `/api/sessions/:id/messages` | Mensagens de uma sessão  |
| POST | `/api/properties/save` | Salvar imóvel |
| POST | `/api/feedback` | Enviar feedback explícito |
| GET | `/api/user/profile` | Perfil do usuário |

### Testes
Cada teste usa `pytest` + `pytest-asyncio`:
- **`test_semantic_router.py`** — classificação correta de intents, compostos, threshold
- **`test_dag_resolver.py`** — DAGs gerados corretamente para cada intent
- **`test_orchestrator.py`** — execução com paralelismo real, fallbacks
- **`test_resilience_manager.py`** — retry, circuit breaker mudando de estado
- **`test_confidence_gate.py`** — bloqueio com properties vazio, passagem com dados completos
- **`test_memory_manager.py`** — cache TTL, sessão, memória de usuário

## Critérios de Aceite

- [ ] Pipeline executa E2E: `python main.py "quero um apartamento de 2 quartos em Goiânia para investir"`
- [ ] Nenhum LLM chamado fora do `ResponseVerbalizer`
- [ ] Circuit breaker muda CLOSED→OPEN após 5 falhas consecutivas
- [ ] DAG composto executa `location_insights` + `valuation` em paralelo
- [ ] `ConfidenceGate` bloqueia LLM quando `properties` está vazio
- [ ] `ContextStore` mantém histórico de patches (imutável)
- [ ] `pytest tests/` — todos passando
- [ ] `ObservabilityLayer` emite WARNING quando `latencia > 8000ms`
- [ ] Frontend com animações Framer Motion funcionais
- [ ] Interface responsiva (sidebar overlay em mobile)

## Outputs
- `main.py` com pipeline completo
- `api.py` com endpoints REST
- Suite de testes passando
- Sistema rodando end-to-end

## Edge Cases
- Frontend sem backend: funcionar com mock data (hook `useChat` com modo mock)
- Backend sem Redis: operar sem cache, log WARNING
- Backend sem Supabase: testes rodam com mocks, sem dependência de infra
- Rate limit do Gemini: retry com backoff no `ResponseVerbalizer`, log WARNING
