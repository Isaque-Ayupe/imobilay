-- ============================================================
-- IMOBILAY — Migration 001: Schema Inicial
-- ============================================================
-- Executar no SQL Editor do Supabase Dashboard.
-- Pré-requisito: extensões uuid-ossp e vector ativadas.
-- ============================================================


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
    explicit_rating INTEGER CHECK (explicit_rating BETWEEN 1 AND 5),
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
    USING (auth.uid() = id);

CREATE POLICY "user vê e edita próprio perfil de investidor"
    ON investor_profiles FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "user vê e edita próprias sessões"
    ON sessions FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "user vê próprias mensagens"
    ON messages FOR ALL
    USING (
        session_id IN (
            SELECT id FROM sessions WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "user vê próprio feedback"
    ON feedback_records FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "user vê próprios imóveis salvos"
    ON saved_properties FOR ALL
    USING (auth.uid() = user_id);


-- ============================================================
-- FUNÇÕES RPC AUXILIARES
-- ============================================================

-- Incrementar contagem de análises do usuário
CREATE OR REPLACE FUNCTION increment_analysis_count(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE user_profiles
    SET analysis_count = analysis_count + 1
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
