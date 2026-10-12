-- ============================================================================
-- migrantEU - DDL Schema para Supabase (PostgreSQL + pgvector)
-- Dimensão vetorial unificada: 768 (Gemini, Ollama e OpenAI MRL)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Criação de tipos enumerados de status
DO $$ BEGIN
    CREATE TYPE notice_status AS ENUM (
        'pendente_aprovacao',
        'aprovado_vigente',
        'expirado'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- 2. Tabela de Configurações Dinâmicas do Sistema (Troca de modelos em runtime)
-- Os usuários administrativos são gerenciados diretamente pelo Supabase Auth (auth.users)
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 3. Tabela de Categorias Dinâmicas de Oportunidades
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    badge_color VARCHAR(30) DEFAULT 'blue',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
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

-- 5. Tabela de Editais e Oportunidades com Chave Estrangeira category_id e Vetor 768d
CREATE TABLE IF NOT EXISTS notices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
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

-- 6. Tabela de Assinantes por E-mail (Usuários Finais - Sem Senha)
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
ON notices (institution_id, category_id, status, end_date);

CREATE INDEX IF NOT EXISTS idx_notices_aprovados_vigentes 
ON notices (category_id, end_date) 
WHERE status = 'aprovado_vigente';

CREATE INDEX IF NOT EXISTS idx_notices_institution_id 
ON notices (institution_id);

CREATE INDEX IF NOT EXISTS idx_notices_category_id 
ON notices (category_id);

CREATE INDEX IF NOT EXISTS idx_categories_slug 
ON categories (slug);

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

DROP TRIGGER IF EXISTS set_timestamp_categories ON categories;
CREATE TRIGGER set_timestamp_categories
BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_institutions ON institutions;
CREATE TRIGGER set_timestamp_institutions
BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_notices ON notices;
CREATE TRIGGER set_timestamp_notices
BEFORE UPDATE ON notices FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_subscribers ON subscribers;
CREATE TRIGGER set_timestamp_subscribers
BEFORE UPDATE ON subscribers FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

-- 9. RPC para busca semântica no Supabase (768 dimensões com join em categories)
CREATE OR REPLACE FUNCTION match_notices (
  query_embedding vector(768),
  match_threshold float DEFAULT 0.60,
  match_count int DEFAULT 5,
  filter_category_id UUID DEFAULT NULL,
  filter_category_slug VARCHAR DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  institution_id UUID,
  institution_name VARCHAR,
  category_id UUID,
  category_slug VARCHAR,
  category_name VARCHAR,
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
    n.category_id,
    c.slug AS category_slug,
    c.name AS category_name,
    n.title,
    n.notice_url,
    n.start_date,
    n.end_date,
    n.summary,
    1 - (n.embedding <=> query_embedding) AS similarity
  FROM notices n
  JOIN institutions i ON n.institution_id = i.id
  JOIN categories c ON n.category_id = c.id
  WHERE n.status = 'aprovado_vigente'
    AND n.end_date >= CURRENT_DATE
    AND (filter_category_id IS NULL OR n.category_id = filter_category_id)
    AND (filter_category_slug IS NULL OR c.slug = filter_category_slug)
    AND 1 - (n.embedding <=> query_embedding) > match_threshold
  ORDER BY n.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
