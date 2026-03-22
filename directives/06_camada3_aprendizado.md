# Directive 06 — Camada 3: Aprendizado e Observabilidade

## Objetivo
Implementar o ciclo de feedback que retroalimenta o sistema: coletar sinais de qualidade, manter memória persistente por usuário, cachear resultados de agentes e recalcular pesos do roteador.

## Inputs
- Especificação em `context/imobilay_back.md` → seção "CAMADA 3"
- Repositories de banco (Directive 03) — para persistir feedback e traces
- Orchestrator funcionando (Directive 05)

## Scripts/Tools
- Nenhum script de execução separado

## Estrutura de Arquivos

```
layer_3_learning/
├── __init__.py
├── feedback_collector.py         ← Sinais explícitos e implícitos
├── memory_manager.py             ← Sessão, usuário, cache
├── observability_layer.py        ← Métricas e alertas
└── router_feedback_loop.py       ← Recalibração do roteador
```

## Especificação por Componente

### 1. `FeedbackCollector`
Captura dois tipos de sinal:

**Explícito:** rating 1-5 do usuário + comentário opcional
**Implícito (inferido das ações seguintes):**
| Ação do usuário | Sinal |
|---|---|
| Follow-up pedindo ajuste | `needs_improvement` |
| Agiu sobre recomendação (salvou, clicou) | `good` |
| Sem resposta após 30s | `uncertain` |

Persiste via `FeedbackRepository`.

### 2. `MemoryManager`
Três tipos de memória com TTLs distintos:

| Tipo | TTL | Storage | Uso |
|---|---|---|---|
| `SessionMemory` | Duração da sessão | Redis/Memória | Filtros, refinamentos, imóveis descartados |
| `UserMemory` | 90 dias | Supabase (`investor_profiles`) | Histórico, perfil investidor, preferências |
| `ResultCache` | Variável | Redis | Cache de agentes (scraper: 15min, location: 24h, valuation: 6h) |

**Chave de cache:** `hash(intent + filtros_normalizados)`

Interface:
```python
get_session(session_id) -> SessionMemory
get_user(user_id) -> UserMemory
update_user(user_id, patch) -> UserMemory
get_cached(cache_key) -> CachedResult | None
set_cached(cache_key, value, ttl_seconds) -> None
```

### 3. `ObservabilityLayer`
Métricas coletadas por execução (`trace_id`):
- `latencia_total_ms`, `latencia_por_agent`
- `taxa_fallback_por_agent` (janela de 1h)
- `confidence_gate_score`
- `intent_detectado`, `intent_confidence`
- `properties_encontradas`, `properties_com_valuation`, `oportunidades_detectadas`

**Alertas automáticos (log WARNING):**
- `latencia_total_ms > 8000`
- `taxa_fallback > 0.3` em janela de 10 execuções
- `confidence_gate_score < 0.5` em mais de 20% das execuções na última hora

Persiste trace completo via `TraceRepository`.

### 4. `RouterFeedbackLoop`
A cada 100 execuções, recalcula pesos dos intents:
```
precision = execuções_sem_fallback_crítico / total_execuções_desse_intent
satisfaction = média(explicit_rating) para esse intent
peso_final = 0.6 * precision + 0.4 * satisfaction
```

Regras adicionais:
- Agente com circuit breaker OPEN por >5min → excluir do próximo DAG + log ERROR
- Intent composto com satisfação maior que simples → baixar threshold de 0.65 para 0.60

## Outputs
- 4 módulos Python funcionais
- Métricas emitindo alertas corretamente
- Cache reduzindo latência em buscas repetidas
- Testes: `test_memory_manager.py`

## Edge Cases
- Redis indisponível: `ResultCache` opera sem cache (fallback: sempre calcular do zero), log WARNING
- `UserMemory` com TTL expirado (>90 dias desde `last_active_at`): deletar dados antigos, criar perfil novo
- Feedback implícito é probabilístico — nunca usar como ground truth isolado, só em agregação
- `RouterFeedbackLoop` com < 100 execuções: não recalcular, usar pesos default
