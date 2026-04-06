---
name: db-migration
description: Criar e aplicar migrations no Supabase do IMOBILAY, incluindo convenções e repositórios.
disable-model-invocation: true
allowed-tools: Bash Read Edit Glob
---

# Migrations — Supabase

## Estrutura

```
supabase/
├── config.toml    # Configuração do projeto Supabase
├── migrations/    # Arquivos SQL de migração
└── Readme.md
```

## Criar nova migration

### 1. Gerar migration com timestamp

```bash
cd /c/imobilay
supabase migration add nome_da_migration
```

Isso cria `supabase/migrations/{TIMESTAMP}_nome_da_migration.sql`.

### 2. Escrever SQL

```sql
-- supabase/migrations/{TIMESTAMP}_nome_da_migration.sql
-- Nome: Descrição clara do que a migration faz

CREATE TABLE IF NOT EXISTS properties (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    location POINT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para queries frequentes
CREATE INDEX idx_properties_location ON properties USING GIST (location);
```

## Aplicar migrations

### Local

```bash
cd /c/imobilay
supabase db start          # Sobe container local
supabase db reset          # Reset + aplica todas migrations
supabase db push           # Aplica migrations pendentes
```

### Remoto (Supabase Cloud)

```bash
supabase link --project-ref <PROJECT_REF>
supabase db push
```

## Repositórios

Repositórios em `database/repositories/` seguem o padrão Repository:

- `database/client.py` — cliente Supabase
- `database/repositories/session_repository.py` — sessões
- Demais repositórios adicionados conforme necessidade

### Padrão de um repositório

```python
from database.client import get_supabase_client

class MeuRepository:
    def __init__(self):
        self.client = get_supabase_client()

    async def create(self, data: dict) -> dict:
        result = self.client.table("minha_tabela").insert(data).execute()
        return result.data[0]

    async def get_by_id(self, id: str) -> dict | None:
        result = self.client.table("minha_tabela").select("*").eq("id", id).execute()
        return result.data[0] if result.data else None
```

## Convenções

1. **Timestamp no nome**: `{YYYYMMDDHHMMSS}_descricao.sql`
2. **Idempotente**: usar `IF NOT EXISTS`, `IF EXISTS` onde possível
3. **Rollback**: sempre pensar em como rollbackar antes de aplicar
4. **Testar local**: rodar `supabase db push` local antes de ir para cloud
5. **RLS**: sempre configurar Row Level Security para tabelas de usuário
