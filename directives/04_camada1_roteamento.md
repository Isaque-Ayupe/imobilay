# Directive 04 — Camada 1: Entrada e Roteamento Semântico

## Objetivo
Implementar os 4 componentes da Camada 1: receber a mensagem do usuário, classificar a intenção sem LLM, resolver o grafo de execução (DAG) e manter o estado compartilhado.

## Inputs
- Especificação completa em `context/imobilay_back.md` → seção "CAMADA 1"
- Models implementados (Directive 02)
- Banco configurado (Directive 03) — para buscar embeddings salvos

## Scripts/Tools
- `execution/seed_intents.py` — popular `intent_embeddings` com vetores de exemplo

## Estrutura de Arquivos

```
layer_1_input/
├── __init__.py
├── input_processor.py        ← InputProcessor
├── semantic_router.py        ← SemanticRouter
├── dag_resolver.py           ← DAGResolver
└── context_store.py          ← SharedContextStore (re-exporta de models)
```

## Especificação por Componente

### 1. `InputProcessor`
```
Entrada: raw_message (str), session_id (str), user_profile (UserProfile | None)
Saída:   ProcessedInput (message, session_id, user_profile, timestamp, trace_id)
```
- Gera `trace_id` (UUID) aqui — propagado por todo o sistema
- Normaliza a mensagem: strip, lowercase para classificação (manter original para display)
- Se `user_profile` é None, criar perfil default

### 2. `SemanticRouter`
```
Entrada: ProcessedInput
Saída:   RoutingResult (primary_intent, secondary_intent, confidence, is_compound, raw_scores)
```

**Estratégia:**
- Usar `sentence-transformers` (modelo: `all-MiniLM-L6-v2`) para gerar embedding da mensagem
- Comparar via cosine similarity contra embeddings pré-computados por intent
- Threshold de confiança: 0.65 para ativar um intent
- Se dois intents > 0.65: gerar intent composto (ex: `buscar_imoveis+investimento`)

**Intents suportados:**
| Intent | Exemplos |
|---|---|
| `buscar_imoveis` | "quero um apartamento em Pinheiros", "procuro 2 quartos até 800k" |
| `analisar_imovel` | "analisa esse imóvel pra mim", "o preço tá bom?" |
| `investimento` | "qual o melhor pra investir?", "quero ROI alto" |
| `refinar_busca` | "agora com 3 quartos", "tira os acima de 1M" |

> **REGRA:** NUNCA usar LLM para classificação de intent. Apenas embedding similarity.

### 3. `DAGResolver`
```
Entrada: RoutingResult
Saída:   ExecutionDAG (nodes, edges, execution_groups, estimated_steps)
```

**Mapeamento de intents → DAGs:**
- `buscar_imoveis`: `[web_scraper] → [normalize] → [location_insights, valuation] (parallel) → [compare_properties]`
- `analisar_imovel`: `[location_insights] → [valuation] → [investment_analysis]`
- `investimento`: `[web_scraper] → [normalize] → [location_insights, valuation] (parallel) → [investment_analysis] → [opportunity_detection] → [compare_properties]`
- `refinar_busca`: `[user_memory] → [web_scraper] → [normalize] → [compare_properties]`

**Intent composto:** merge dos dois DAGs com deduplicação de nodes e resolução de conflitos de ordem.

**Tipos de edge:**
- PARALLEL — nodes sem dependência mútua
- SEQUENTIAL — output de um é input do próximo
- CONDITIONAL — ativado se predicado do node anterior for verdadeiro

### 4. `SharedContextStore`
O ContextStore em si está em `models/context.py`. Este módulo apenas re-exporta e adiciona helpers de fábrica:
- `create_initial_context(processed_input)` → retorna ContextStore vazio com input preenchido

## Outputs
- 4 módulos Python funcionais
- `seed_intents.py` executado para popular embeddings de exemplo
- Testes: `test_semantic_router.py`, `test_dag_resolver.py`

## Edge Cases
- Se `sentence-transformers` não estiver disponível: fallback com keyword matching + TF-IDF
- Intent com confiança < 0.4: retornar mensagem pedindo mais detalhes (não executar pipeline)
- Mensagem vazia ou muito curta (< 3 palavras): pedir clarificação
- DAG composto com conflito de ordem: priorizar o intent com maior confidence
- `trace_id` deve ser UUIDv4 puro, sem prefixo
