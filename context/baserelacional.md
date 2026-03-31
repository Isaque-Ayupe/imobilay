# IMOBILAY — Base Relacional (Supabase / PostgreSQL)

> **Para uso do Gemini 2.5 Pro:** Este documento é a referência completa da camada de dados relacionais do IMOBILAY. Contém o schema SQL, arquitetura de conexão, padrões de acesso, políticas de segurança e código de integração com o pipeline multi-agente. Leia integralmente antes de implementar qualquer módulo que interaja com o banco.

---

## 1. Visão Geral da Arquitetura

O IMOBILAY usa **Supabase (PostgreSQL gerenciado)** para todos os dados relacionais persistidos:
usuários, sessões de conversa, histórico de mensagens, traces de execução, feedback e imóveis salvos.

### O que pertence a esta camada

| Dado | Justificativa |
|---|---|
| `user_profiles` | Persistência longa, relações com todas as entidades |
| `investor_profiles` | Memória de longo prazo do usuário (TTL 90 dias) |
| `sessions` | Histórico de conversas agrupado por usuário |
| `messages` | Cada turno de conversa com link ao trace de execução |
| `execution_traces` | Rastreabilidade completa do pipeline (ObservabilityLayer) |
| `feedback_records` | Sinais explícitos e implícitos de qualidade |
| `saved_properties` | Imóveis salvos pelo usuário como snapshot JSONB |
| `intent_embeddings` | Vetores do SemanticRouter (via pgvector) |

### O que NÃO pertence a esta camada

| Dado | Onde vai | Motivo |
|---|---|---|
| Cache de scraping (TTL 15min) | Redis / Upstash | Expiração automática, sub-ms |
| Estado do Circuit Breaker | Redis / Upstash | Contador em janela de tempo |
| `ContextStore` durante execução | Memória Python in-process | Nunca persiste durante o pipeline |
| Sessão ativa de conversa (TTL sessão) | Redis / Memória | Temporário, não relacional |

---

## 2. Variáveis de Ambiente

### `.env.example` (commitar no git)
```bash
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxx
SUPABASE_SERVICE_ROLE_KEY=seu-service-role-key-aqui
```

### `.env` (NUNCA commitar — adicionar ao `.gitignore`)
```bash
SUPABASE_URL=https://xyzabcdef.supabase.co
SUPABASE_ANON_KEY=sb_publishable_...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

### Onde encontrar no Supabase Dashboard
```
Project Settings → API → Project URL
Project Settings → API → Project API keys → anon (public)
Project Settings → API → Project API keys → service_role (secret)
```

> **ATENÇÃO:** A `service_role` key bypassa o Row Level Security. Usada APENAS no backend pelos agentes do pipeline. Nunca exposta no frontend.

---

## 3. Schema SQL Completo

Execute no **SQL Editor do Supabase Dashboard** ou via migration file.

### `database/migrations/001_initial.sql`

```sql
-- ============================================================
-- EXTENSÕES
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;        -- para embeddings do SemanticRouter


-- ============================================================
-- TABELA: user_profiles
-- Extensão do auth.users do Supabase com dados de produto
-- ============================================================
CREATE TABLE user_profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    plan            TEXT NOT NULL DEFAULT 'free'
                        CHECK (plan IN ('free', 'pro', 'elite')),
    analysis_count  INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger para sincronizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ============================================================
-- TABELA: investor_profiles
-- Memória de longo prazo do usuário (Camada 3 — MemoryManager)
-- TTL lógico: 90 dias (enforçado na aplicação, não no banco)
-- ============================================================
CREATE TABLE investor_profiles (
    user_id             UUID PRIMARY KEY
                            REFERENCES user_profiles(id) ON DELETE CASCADE,
    risk_tolerance      TEXT CHECK (risk_tolerance IN ('low', 'medium', 'high')),
    horizon_years       INTEGER CHECK (horizon_years > 0),
    estimated_capital   NUMERIC CHECK (estimated_capital >= 0),
    preferred_areas     TEXT[],           -- ex: ['Pinheiros', 'Vila Madalena']
    price_min           NUMERIC CHECK (price_min >= 0),
    price_max           NUMERIC CHECK (price_max >= 0),
    preferred_types     TEXT[],           -- ex: ['apartamento', 'studio']
    investment_goal     TEXT CHECK (investment_goal IN ('rental', 'appreciation', 'both')),
    last_active_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_investor_profiles_updated_at
    BEFORE UPDATE ON investor_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- ============================================================
-- TABELA: sessions
-- Cada conversa com o IMOBILAY é uma sessão
-- ============================================================
CREATE TABLE sessions (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    title       TEXT,                     -- gerado da 1ª mensagem do usuário
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- TABELA: messages
-- Cada turno de conversa (user ou assistant)
-- ============================================================
CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id  UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    trace_id    UUID,                     -- link para execution_traces (nullable: msg do user não tem trace)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- TABELA: execution_traces
-- Rastreabilidade completa de cada execução do pipeline
-- Gerado pela ObservabilityLayer (Camada 3)
-- O trace_id é gerado no InputProcessor e propagado por todo o sistema
-- ============================================================
CREATE TABLE execution_traces (
    trace_id                UUID PRIMARY KEY,
    session_id              UUID REFERENCES sessions(id) ON DELETE SET NULL,
    user_id                 UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    intent_detected         TEXT,
    intent_confidence       FLOAT CHECK (intent_confidence BETWEEN 0 AND 1),
    is_compound_intent      BOOLEAN DEFAULT FALSE,
    confidence_gate_score   FLOAT CHECK (confidence_gate_score BETWEEN 0 AND 1),
    confidence_gate_passed  BOOLEAN,
    properties_found        INTEGER DEFAULT 0,
    properties_with_valuation INTEGER DEFAULT 0,
    opportunities_detected  INTEGER DEFAULT 0,
    latency_total_ms        INTEGER,
    latency_per_agent       JSONB,        -- ex: {"web_scraper": 1200, "valuation": 340}
    agents_used             TEXT[],
    agents_failed           TEXT[],
    agents_skipped          TEXT[],
    dag_execution_groups    INTEGER,      -- quantos grupos paralelos foram executados
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- TABELA: feedback_records
-- Sinais de qualidade explícitos e implícitos (Camada 3 — FeedbackCollector)
-- ============================================================
CREATE TABLE feedback_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trace_id        UUID REFERENCES execution_traces(trace_id) ON DELETE CASCADE,
    user_id         UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    session_id      UUID REFERENCES sessions(id) ON DELETE SET NULL,
    explicit_rating INTEGER CHECK (explicit_rating BETWEEN 1 AND 5),   -- nullable: nem sempre preenchido
    implicit_signal TEXT CHECK (implicit_signal IN ('good', 'needs_improvement', 'uncertain')),
    intent_original TEXT,
    agents_used     TEXT[],
    agents_failed   TEXT[],
    total_duration_ms INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- TABELA: saved_properties
-- Imóveis salvos pelo usuário como snapshot imutável
-- Usa JSONB para preservar o estado exato da PropertyAnalysis no momento do salvamento
-- ============================================================
CREATE TABLE saved_properties (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    trace_id        UUID REFERENCES execution_traces(trace_id) ON DELETE SET NULL,
    property_data   JSONB NOT NULL,       -- snapshot completo da PropertyAnalysis
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- TABELA: intent_embeddings
-- Vetores pré-computados para o SemanticRouter (Camada 1)
-- Usa pgvector com dimensão 384 (all-MiniLM-L6-v2)
-- ============================================================
CREATE TABLE intent_embeddings (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intent_name TEXT NOT NULL,            -- ex: 'buscar_imoveis', 'investimento'
    example_text TEXT NOT NULL,           -- texto de exemplo que gerou o embedding
    embedding   vector(384) NOT NULL,     -- gerado por sentence-transformers
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice HNSW para busca por similaridade eficiente
CREATE INDEX idx_intent_embeddings_hnsw
    ON intent_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);


-- ============================================================
-- ÍNDICES DE PERFORMANCE
-- ============================================================
CREATE INDEX idx_sessions_user_id          ON sessions(user_id);
CREATE INDEX idx_sessions_last_active      ON sessions(last_active DESC);
CREATE INDEX idx_messages_session_id       ON messages(session_id);
CREATE INDEX idx_messages_created_at       ON messages(created_at);
CREATE INDEX idx_traces_user_id            ON execution_traces(user_id);
CREATE INDEX idx_traces_session_id         ON execution_traces(session_id);
CREATE INDEX idx_traces_created_at         ON execution_traces(created_at DESC);
CREATE INDEX idx_feedback_trace_id         ON feedback_records(trace_id);
CREATE INDEX idx_feedback_user_id          ON feedback_records(user_id);
CREATE INDEX idx_saved_user_id             ON saved_properties(user_id);
CREATE INDEX idx_saved_created_at          ON saved_properties(created_at DESC);
CREATE INDEX idx_intent_name               ON intent_embeddings(intent_name);


-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE user_profiles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE investor_profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions            ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages            ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_records    ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_properties    ENABLE ROW LEVEL SECURITY;
-- execution_traces e intent_embeddings: acesso apenas via service_role (sem RLS de usuário)

-- Policies: cada usuário só acessa seus próprios dados
CREATE POLICY "user vê e edita próprio perfil"
    ON user_profiles FOR ALL
    USING ((select auth.uid()) = id);

CREATE POLICY "user vê e edita próprio perfil de investidor"
    ON investor_profiles FOR ALL
    USING ((select auth.uid()) = user_id);

CREATE POLICY "user vê e edita próprias sessões"
    ON sessions FOR ALL
    USING ((select auth.uid()) = user_id);

CREATE POLICY "user vê próprias mensagens"
    ON messages FOR ALL
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = (select auth.uid())
        )
    );

CREATE POLICY "user vê próprio feedback"
    ON feedback_records FOR ALL
    USING ((select auth.uid()) = user_id);

CREATE POLICY "user vê próprios imóveis salvos"
    ON saved_properties FOR ALL
    USING ((select auth.uid()) = user_id);
```

---

## 4. Configuração da Conexão Python

### Dependências

Adicionar ao `requirements.txt`:
```
supabase>=2.10.0
python-dotenv>=1.0.0
```

### `database/client.py`

```python
"""
Cliente Supabase para o IMOBILAY.

Dois clientes distintos por design:
  - system_client: usa service_role, bypassa RLS, usado pelos agentes do pipeline
  - user_client:   usa anon_key + JWT do usuário, respeita RLS, usado em operações de leitura do frontend

O sistema é 100% async (asyncio) — usar SEMPRE AsyncClient.
A conexão via Transaction Mode (porta 6543 via Supavisor) libera a conexão após cada query,
maximizando concorrência nos pipelines paralelos do orquestrador.
"""

import os
from supabase._async.client import AsyncClient
from supabase._async.client import create_client as acreate_client
from dotenv import load_dotenv

load_dotenv()

# ── Singleton do cliente de sistema ──────────────────────────
_system_client: AsyncClient | None = None


async def get_system_client() -> AsyncClient:
    """
    Retorna o cliente com service_role key.
    Singleton — criado uma vez e reutilizado por todo o processo.
    Usar para: agentes do pipeline, ObservabilityLayer, FeedbackCollector, RouterFeedbackLoop.
    """
    global _system_client
    if _system_client is None:
        _system_client = await acreate_client(
            supabase_url=os.environ["SUPABASE_URL"],
            supabase_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
    return _system_client


async def get_user_client(user_jwt: str) -> AsyncClient:
    """
    Retorna cliente com contexto de usuário autenticado.
    NÃO é singleton — cada request recebe sua própria instância para evitar
    vazamento de sessão entre usuários diferentes.
    Usar para: leitura de histórico, perfil, imóveis salvos via frontend.
    """
    client = await acreate_client(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_key=os.environ["ANON_KEY"],
    )
    await client.auth.set_session(
        access_token=user_jwt,
        refresh_token="",
    )
    return client
```

---

## 5. Repository Pattern — Implementação Completa

Cada entidade tem seu próprio repository. Os agentes e a Camada 3 usam repositórios, nunca acessam o cliente diretamente.

### `database/repositories/user_repository.py`

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class UserProfile:
    id: UUID
    name: str
    plan: str
    analysis_count: int
    created_at: datetime
    updated_at: datetime


class UserRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def get_by_id(self, user_id: str) -> UserProfile | None:
        result = await (
            self._db.table("user_profiles")
            .select("*")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
        return self._map(result.data) if result.data else None

    async def create(self, user_id: str, name: str) -> UserProfile:
        result = await (
            self._db.table("user_profiles")
            .insert({"id": user_id, "name": name})
            .execute()
        )
        return self._map(result.data[0])

    async def increment_analysis_count(self, user_id: str) -> None:
        await self._db.rpc(
            "increment_analysis_count",
            {"p_user_id": user_id}
        ).execute()

    def _map(self, row: dict) -> UserProfile:
        return UserProfile(
            id=UUID(row["id"]),
            name=row["name"],
            plan=row["plan"],
            analysis_count=row["analysis_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
```

### `database/repositories/session_repository.py`

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class SessionRecord:
    id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime
    last_active: datetime


class SessionRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def create(self, user_id: str, title: str | None = None) -> SessionRecord:
        result = await (
            self._db.table("sessions")
            .insert({"user_id": user_id, "title": title})
            .execute()
        )
        return self._map(result.data[0])

    async def list_by_user(
        self, user_id: str, limit: int = 50
    ) -> list[SessionRecord]:
        result = await (
            self._db.table("sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("last_active", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    async def update_last_active(self, session_id: str) -> None:
        await (
            self._db.table("sessions")
            .update({"last_active": datetime.utcnow().isoformat()})
            .eq("id", session_id)
            .execute()
        )

    async def update_title(self, session_id: str, title: str) -> None:
        await (
            self._db.table("sessions")
            .update({"title": title})
            .eq("id", session_id)
            .execute()
        )

    def _map(self, row: dict) -> SessionRecord:
        return SessionRecord(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            title=row.get("title"),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_active=datetime.fromisoformat(row["last_active"]),
        )
```

### `database/repositories/trace_repository.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class TraceRecord:
    trace_id: UUID
    session_id: UUID | None
    user_id: UUID | None
    intent_detected: str | None
    intent_confidence: float | None
    confidence_gate_score: float | None
    confidence_gate_passed: bool | None
    properties_found: int
    opportunities_detected: int
    latency_total_ms: int | None
    agents_used: list[str]
    agents_failed: list[str]
    created_at: datetime


class TraceRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def save(self, trace: TraceRecord) -> None:
        """
        Persiste o ExecutionTrace ao final do pipeline.
        Chamado pela ObservabilityLayer após todas as fases concluírem.
        """
        await (
            self._db.table("execution_traces")
            .insert({
                "trace_id":                 str(trace.trace_id),
                "session_id":               str(trace.session_id) if trace.session_id else None,
                "user_id":                  str(trace.user_id) if trace.user_id else None,
                "intent_detected":          trace.intent_detected,
                "intent_confidence":        trace.intent_confidence,
                "confidence_gate_score":    trace.confidence_gate_score,
                "confidence_gate_passed":   trace.confidence_gate_passed,
                "properties_found":         trace.properties_found,
                "opportunities_detected":   trace.opportunities_detected,
                "latency_total_ms":         trace.latency_total_ms,
                "agents_used":              trace.agents_used,
                "agents_failed":            trace.agents_failed,
            })
            .execute()
        )

    async def get_recent_by_user(
        self, user_id: str, limit: int = 100
    ) -> list[TraceRecord]:
        """Usado pelo RouterFeedbackLoop para calcular métricas por intent."""
        result = await (
            self._db.table("execution_traces")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    async def get_for_feedback_cycle(self, limit: int = 100) -> list[TraceRecord]:
        """
        Usado pelo RouterFeedbackLoop a cada 100 execuções.
        Busca traces recentes de todos os usuários para recalcular pesos.
        Requer service_role (sem filtro de user_id).
        """
        result = await (
            self._db.table("execution_traces")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [self._map(r) for r in result.data]

    def _map(self, row: dict) -> TraceRecord:
        return TraceRecord(
            trace_id=UUID(row["trace_id"]),
            session_id=UUID(row["session_id"]) if row.get("session_id") else None,
            user_id=UUID(row["user_id"]) if row.get("user_id") else None,
            intent_detected=row.get("intent_detected"),
            intent_confidence=row.get("intent_confidence"),
            confidence_gate_score=row.get("confidence_gate_score"),
            confidence_gate_passed=row.get("confidence_gate_passed"),
            properties_found=row.get("properties_found", 0),
            opportunities_detected=row.get("opportunities_detected", 0),
            latency_total_ms=row.get("latency_total_ms"),
            agents_used=row.get("agents_used") or [],
            agents_failed=row.get("agents_failed") or [],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
```

### `database/repositories/feedback_repository.py`

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from supabase._async.client import AsyncClient


@dataclass
class FeedbackRecord:
    trace_id: UUID
    user_id: UUID
    session_id: UUID | None
    explicit_rating: int | None
    implicit_signal: str
    intent_original: str | None
    agents_used: list[str]
    agents_failed: list[str]
    total_duration_ms: int | None


class FeedbackRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def save(self, record: FeedbackRecord) -> None:
        await (
            self._db.table("feedback_records")
            .insert({
                "trace_id":         str(record.trace_id),
                "user_id":          str(record.user_id),
                "session_id":       str(record.session_id) if record.session_id else None,
                "explicit_rating":  record.explicit_rating,
                "implicit_signal":  record.implicit_signal,
                "intent_original":  record.intent_original,
                "agents_used":      record.agents_used,
                "agents_failed":    record.agents_failed,
                "total_duration_ms": record.total_duration_ms,
            })
            .execute()
        )

    async def get_by_intent(self, intent: str, limit: int = 100) -> list[dict]:
        """Usado pelo RouterFeedbackLoop para calcular satisfaction por intent."""
        result = await (
            self._db.table("feedback_records")
            .select("explicit_rating, implicit_signal, agents_failed")
            .eq("intent_original", intent)
            .not_.is_("explicit_rating", "null")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
```

---

## 6. Integração com o Pipeline Multi-Agente

### Como o `trace_id` percorre o sistema

```
InputProcessor (Camada 1)
  └── gera trace_id (UUID) → propaga para ProcessedInput

Orchestrator (Camada 2)
  └── trace_id presente no ContextStore desde o início
  └── cada AgentExecutionRecord carrega o mesmo trace_id

ObservabilityLayer (Camada 3)
  └── ao final do pipeline, chama TraceRepository.save(trace)
  └── o trace_id vira a chave que une execution_traces ↔ messages ↔ feedback_records
```

### Exemplo de uso no `main.py`

```python
import asyncio
from database.client import get_system_client
from database.repositories.session_repository import SessionRepository
from database.repositories.trace_repository import TraceRepository
from database.repositories.feedback_repository import FeedbackRepository

async def run_pipeline(message: str, user_id: str, session_id: str | None = None):
    db = await get_system_client()

    sessions = SessionRepository(db)
    traces   = TraceRepository(db)

    # Cria nova sessão se não existir
    if session_id is None:
        session = await sessions.create(user_id=user_id)
        session_id = str(session.id)
    else:
        await sessions.update_last_active(session_id)

    # --- pipeline executa aqui ---
    # O trace_id é gerado no InputProcessor e retorna no OrchestratorResult
    # orchestrator_result = await orchestrator.execute(...)

    # Ao final, persiste o trace
    # await traces.save(orchestrator_result.to_trace_record(session_id, user_id))
```

### Ponto de persistência por componente

| Componente | Quando acessa o banco | Repositório |
|---|---|---|
| `InputProcessor` | Nunca — só gera trace_id | — |
| `MemoryManager` | Leitura de `investor_profiles` no início | `UserRepository` |
| `Orchestrator` | Nunca diretamente | — |
| `ObservabilityLayer` | Escrita ao final de cada execução | `TraceRepository` |
| `FeedbackCollector` | Escrita ao receber sinal (explícito ou implícito) | `FeedbackRepository` |
| `RouterFeedbackLoop` | Leitura em lote a cada 100 execuções | `TraceRepository`, `FeedbackRepository` |
| `ResponseVerbalizer` | Nunca — só usa ContextStore em memória | — |

---

## 7. Checklist de Setup no Supabase Dashboard

Execute nesta ordem antes de rodar qualquer código:

```
[ ] 1. Project Settings → API
        Copiar SUPABASE_URL para .env
        Copiar anon key para .env (SUPABASE_ANON_KEY)
        Copiar service_role key para .env (SUPABASE_SERVICE_ROLE_KEY)

[ ] 2. Database → Extensions
        Ativar: uuid-ossp
        Ativar: vector (pgvector)

[ ] 3. SQL Editor
        Executar: database/migrations/001_initial.sql
        Verificar: todas as tabelas criadas sem erro
        Verificar: índice HNSW em intent_embeddings criado

[ ] 4. Authentication → Providers
        Ativar: Email (para auth nativo de usuários)

[ ] 5. Database → Connection Pooling
        Confirmar: Pool Mode = Transaction
        Confirmar: porta usada = 6543 (não 5432)

[ ] 6. Testar conexão
        python -c "import asyncio; from database.client import get_system_client; asyncio.run(get_system_client())"
```

---

## 8. Regras de Implementação para o Gemini 2.5 Pro

> Estas regras são restrições de design, não sugestões. Seguir à risca.

**R1 — Dois clientes, propósitos separados**
O `system_client` (service_role) é exclusivo para agentes de pipeline e Camada 3.
O `user_client` (anon + JWT) é exclusivo para operações com contexto de usuário.
Nunca usar service_role para operações iniciadas pelo frontend.

**R2 — ContextStore nunca vai ao banco durante execução**
O estado imutável com patches vive em memória Python do início ao fim do pipeline.
Apenas o `ExecutionTrace` final é persistido, após o `ConfidenceGate` e o `ResponseVerbalizer` concluírem.

**R3 — Repositórios são a única interface com o banco**
Nenhum agente, nenhum componente da Camada 3, nenhuma função em `main.py`
executa queries diretamente no cliente Supabase.
Toda interação passa por um método de repositório.

**R4 — AsyncClient obrigatório em todo o sistema**
O orquestrador usa `asyncio.gather()` para paralelismo.
Usar cliente síncrono em qualquer ponto bloqueia o event loop e quebra o paralelismo.

**R5 — IDs são UUIDs, não strings**
Os dataclasses de retorno dos repositórios usam `UUID` (Python).
A serialização para string (`str(uuid)`) só acontece no momento de inserção no banco.

**R6 — Erros de banco são `AgentError`, não exceções nuas**
Qualquer falha de I/O com o banco deve ser capturada, convertida em `AgentError`
com `severity="ERROR"` e registrada no `ContextStore.errors`.
O sistema não para por falha de persistência.

**R7 — `saved_properties.property_data` é snapshot imutável**
O campo JSONB guarda o estado exato da `PropertyAnalysis` no momento do salvamento.
Nunca atualizar esse campo depois — criar novo registro se necessário.

---

## 9. Estrutura de Arquivos da Camada de Dados

```
imobilay/
├── .env                                ← nunca commitar
├── .env.example                        ← commitar
├── database/
│   ├── __init__.py
│   ├── client.py                       ← get_system_client(), get_user_client()
│   ├── migrations/
│   │   └── 001_initial.sql             ← schema completo (seção 3 deste doc)
│   └── repositories/
│       ├── __init__.py
│       ├── user_repository.py          ← UserRepository
│       ├── session_repository.py       ← SessionRepository
│       ├── message_repository.py       ← MessageRepository
│       ├── trace_repository.py         ← TraceRepository
│       ├── feedback_repository.py      ← FeedbackRepository
│       ├── saved_property_repository.py ← SavedPropertyRepository
│       └── investor_profile_repository.py ← InvestorProfileRepository
```

---

*Documento gerado para o IMOBILAY — base relacional v1.0*
*Stack: Supabase (PostgreSQL 15) + pgvector + supabase-py AsyncClient*
