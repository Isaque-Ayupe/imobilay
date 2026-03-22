# Directive 03 — Banco de Dados (Supabase + PostgreSQL)

## Objetivo
Configurar a camada de dados relacional completa: executar migrations, implementar o cliente async e todos os repositories com o Repository Pattern.

## Inputs
- Especificação completa em `context/baserelacional.md`
- Supabase Dashboard configurado (Directive 01)
- Models implementados (Directive 02)

## Scripts/Tools
- `execution/run_migrations.py` — executa o SQL no Supabase
- `execution/test_connection.py` — valida conexão e existência das tabelas

## Estrutura de Arquivos

```
database/
├── __init__.py
├── client.py                        ← get_system_client(), get_user_client()
├── migrations/
│   └── 001_initial.sql              ← Schema completo (copiar da seção 3 do baserelacional.md)
└── repositories/
    ├── __init__.py
    ├── user_repository.py           ← UserRepository
    ├── session_repository.py        ← SessionRepository
    ├── message_repository.py        ← MessageRepository
    ├── trace_repository.py          ← TraceRepository
    ├── feedback_repository.py       ← FeedbackRepository
    ├── saved_property_repository.py ← SavedPropertyRepository
    └── investor_profile_repository.py ← InvestorProfileRepository
```

## Especificação

### `database/client.py`
Dois clientes com propósitos separados:
- **`get_system_client()`** — Singleton, service_role key, bypassa RLS. Usado pelos agentes e Camada 3.
- **`get_user_client(jwt)`** — Uma instância por request, anon key + JWT. Usado pelo frontend.

> **REGRA R4:** AsyncClient obrigatório. Nunca usar cliente síncrono.

### Migrations (`001_initial.sql`)
Tabelas a criar:
1. `user_profiles` — com trigger `update_updated_at`
2. `investor_profiles` — TTL lógico 90 dias
3. `sessions` — cada conversa
4. `messages` — cada turno com link ao trace
5. `execution_traces` — rastreabilidade do pipeline
6. `feedback_records` — sinais de qualidade
7. `saved_properties` — snapshot JSONB imutável
8. `intent_embeddings` — vetores pgvector(384) com índice HNSW

Extensões: `uuid-ossp`, `vector`
RLS ativado em: `user_profiles`, `investor_profiles`, `sessions`, `messages`, `feedback_records`, `saved_properties`

### Repositories
Cada repository segue o padrão:
```python
class XxxRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def get_by_id(self, id: str) -> Model | None: ...
    async def create(self, **kwargs) -> Model: ...
    async def update(self, id: str, **kwargs) -> None: ...

    def _map(self, row: dict) -> Model: ...  # conversão de row para dataclass
```

## Outputs
- `001_initial.sql` com schema completo
- `client.py` com dois clientes async
- 7 repositories com CRUD completo
- Testes: `test_connection.py` passando

## Edge Cases
- **R6:** Erros de I/O com o banco → capturar, converter em `AgentError(severity="ERROR")`, registrar no `ContextStore.errors`
- **R5:** IDs são `UUID` nos dataclasses, `str(uuid)` apenas na inserção
- **R7:** `saved_properties.property_data` é snapshot imutável — nunca atualizar, criar novo registro
- Se `pgvector` falhar: o `SemanticRouter` pode operar com fallback em memória (cosine similarity via numpy)
- Connection pool exausto: implementar retry com backoff na `get_system_client()`
