-- ============================================================================
-- migrantEU - DDL Schema para Supabase (PostgreSQL + pgvector)
-- Dimensão vetorial unificada: 768 (Gemini, Ollama e OpenAI MRL)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Criação de tipos enumerados
DO $$ BEGIN
    CREATE TYPE notice_category AS ENUM (
        'ensino_superior',
        'curso_portugues',
        'acolhimento_social',
        'pos_graduacao'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE notice_status AS ENUM (
        'pendente_aprovacao',
        'aprovado_vigente',
        'expirado'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'admin',
        'moderador'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- 2. Tabela de Usuários do Sistema (Backoffice / Operadores / Administradores)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role user_role NOT NULL DEFAULT 'moderador',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 3. Tabela de Configurações Dinâmicas do Sistema (Troca de modelos em runtime)
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 4. Tabela de Instituições Oficiais
CREATE TABLE IF NOT EXISTS institutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    sigla VARCHAR(50),
    uf VARCHAR(2) NOT NULL,
    city VARCHAR(150),
    website_url TEXT NOT NULL,
    official_domain VARCHAR(150) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 5. Tabela de Editais e Oportunidades com Vetor de 768 dimensões
CREATE TABLE IF NOT EXISTS notices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    category notice_category NOT NULL,
    title VARCHAR(300) NOT NULL,
    notice_url TEXT NOT NULL,
    start_date DATE,
    end_date DATE NOT NULL,
    summary TEXT NOT NULL,
    status notice_status NOT NULL DEFAULT 'pendente_aprovacao',
    embedding vector(768), -- Dimensão vetorial unificada em 768
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 6. Tabela de Assinantes por E-mail
CREATE TABLE IF NOT EXISTS subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    topics TEXT[] NOT NULL DEFAULT '{}',
    uf_preference VARCHAR(2),
    magic_token UUID NOT NULL DEFAULT uuid_generate_v4(),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 7. Índices de Otimização e Cache
CREATE INDEX IF NOT EXISTS idx_notices_cache_lookup 
ON notices (institution_id, category, status, end_date);

CREATE INDEX IF NOT EXISTS idx_notices_aprovados_vigentes 
ON notices (category, end_date) 
WHERE status = 'aprovado_vigente';

CREATE INDEX IF NOT EXISTS idx_notices_institution_id 
ON notices (institution_id);

CREATE INDEX IF NOT EXISTS idx_institutions_official_domain 
ON institutions (official_domain);

-- NOTA DE PERFORMANCE: Em fase inicial e MVP, a busca exata (flat/sequential scan)
-- garante 100% de recall, resposta ultrarrápida (<5ms para centenas/milhares de editais)
-- e elimina o overhead de construção de grafo em memória a cada inserção.
-- O índice aproximado HNSW só deve ser criado quando o volume de dados justificar:
--
-- CREATE INDEX IF NOT EXISTS idx_notices_embedding_hnsw_768 
-- ON notices USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);

-- 8. Trigger para updated_at automático
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = TIMEZONE('utc', NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_timestamp_users ON users;
CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_institutions ON institutions;
CREATE TRIGGER set_timestamp_institutions
BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_notices ON notices;
CREATE TRIGGER set_timestamp_notices
BEFORE UPDATE ON notices FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_subscribers ON subscribers;
CREATE TRIGGER set_timestamp_subscribers
BEFORE UPDATE ON subscribers FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

-- 9. RPC para busca semântica no Supabase (768 dimensões)
CREATE OR REPLACE FUNCTION match_notices (
  query_embedding vector(768),
  match_threshold float DEFAULT 0.60,
  match_count int DEFAULT 5,
  filter_category notice_category DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  institution_id UUID,
  institution_name VARCHAR,
  category notice_category,
  title VARCHAR,
  notice_url TEXT,
  start_date DATE,
  end_date DATE,
  summary TEXT,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    n.id,
    n.institution_id,
    i.name AS institution_name,
    n.category,
    n.title,
    n.notice_url,
    n.start_date,
    n.end_date,
    n.summary,
    1 - (n.embedding <=> query_embedding) AS similarity
  FROM notices n
  JOIN institutions i ON n.institution_id = i.id
  WHERE n.status = 'aprovado_vigente'
    AND n.end_date >= CURRENT_DATE
    AND (filter_category IS NULL OR n.category = filter_category)
    AND 1 - (n.embedding <=> query_embedding) > match_threshold
  ORDER BY n.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
