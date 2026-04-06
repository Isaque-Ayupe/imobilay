-- ============================================================
-- IMOBILAY — Migration 002: Tabela de Propriedades
-- ============================================================
-- Cache de imóveis para busca pelo WebScraperAgent.
-- Dados reais coletados de portais imobiliários e fontes públicas.
-- ============================================================

CREATE TABLE properties_cache (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           TEXT NOT NULL,
    price           NUMERIC NOT NULL CHECK (price > 0),
    area_m2         NUMERIC CHECK (area_m2 > 0),
    rooms           INTEGER CHECK (rooms >= 0),
    parking_spaces  INTEGER DEFAULT 0,
    address         TEXT,
    neighborhood    TEXT NOT NULL,
    city            TEXT NOT NULL DEFAULT 'São Paulo',
    state           TEXT NOT NULL DEFAULT 'SP',
    url             TEXT,
    source          TEXT NOT NULL DEFAULT 'database'
                        CHECK (source IN ('zap', 'vivareal', 'olx', 'database', 'other')),
    property_type   TEXT NOT NULL DEFAULT 'apartamento'
                        CHECK (property_type IN (
                            'apartamento', 'studio', 'cobertura', 'kitnet',
                            'casa', 'sobrado', 'terreno', 'comercial'
                        )),
    description     TEXT,
    raw_data        JSONB,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para buscas comuns
CREATE INDEX idx_properties_cache_city ON properties_cache(city);
CREATE INDEX idx_properties_cache_neighborhood ON properties_cache(neighborhood);
CREATE INDEX idx_properties_cache_price ON properties_cache(price);
CREATE INDEX idx_properties_cache_rooms ON properties_cache(rooms);
CREATE INDEX idx_properties_cache_active ON properties_cache(active);
CREATE INDEX idx_properties_cache_city_neighborhood ON properties_cache(city, neighborhood);
CREATE INDEX idx_properties_cache_price_range ON properties_cache(price, city);

-- Trigger para updated_at
CREATE TRIGGER trg_properties_cache_updated_at
    BEFORE UPDATE ON properties_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- RLS: sem RLS nesta tabela, acesso apenas via service_role
-- (dados públicos de mercado, não dados de usuário)
