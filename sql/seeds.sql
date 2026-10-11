-- ============================================================================
-- migrantEU - Seeds Iniciais (Instituições Cátedra Sérgio Vieira de Mello & Apoio)
-- ============================================================================

-- Usuário Admin Padrão (senha padrão provisória: admin123)
-- Hash bcrypt para 'admin123'
INSERT INTO users (email, hashed_password, full_name, role, is_active)
VALUES (
    'admin@migranteu.org',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQmG6KA5W5IDh0vVwX1.G',
    'Administrador migrantEU',
    'admin',
    true
)
ON CONFLICT (email) DO NOTHING;

-- Configuração inicial de IA em system_settings
INSERT INTO system_settings (key, value)
VALUES (
    'ai_config',
    '{
        "llm_provider": "google",
        "llm_model": "gemini-1.5-flash",
        "embedding_provider": "google",
        "embedding_model": "models/text-embedding-004",
        "embedding_dimensions": 768
    }'::jsonb
)
ON CONFLICT (key) DO NOTHING;

-- Instituições Oficiais Parceiras (Universidades CSVM e Entidades de Acolhimento)
INSERT INTO institutions (name, sigla, uf, city, website_url, official_domain, is_active) VALUES
('Universidade Federal do Paraná', 'UFPR', 'PR', 'Curitiba', 'https://www.ufpr.br', 'ufpr.br', true),
('Universidade de São Paulo', 'USP', 'SP', 'São Paulo', 'https://www.usp.br', 'usp.br', true),
('Universidade Estadual de Campinas', 'UNICAMP', 'SP', 'Campinas', 'https://www.unicamp.br', 'unicamp.br', true),
('Universidade Federal de Santa Catarina', 'UFSC', 'SC', 'Florianópolis', 'https://www.ufsc.br', 'ufsc.br', true),
('Universidade Federal do Rio Grande do Sul', 'UFRGS', 'RS', 'Porto Alegre', 'https://www.ufrgs.br', 'ufrgs.br', true),
('Universidade de Brasília', 'UnB', 'DF', 'Brasília', 'https://www.unb.br', 'unb.br', true),
('Cáritas Arquidiocesana de São Paulo', 'Cáritas SP', 'SP', 'São Paulo', 'https://caritassp.org.br', 'caritassp.org.br', true),
('Alto Comissariado das Nações Unidas para Refugiados', 'ACNUR Brasil', 'DF', 'Brasília', 'https://www.acnur.org/portugues', 'acnur.org', true),
('Organização Internacional para as Migrações', 'OIM Brasil', 'DF', 'Brasília', 'https://brazil.iom.int', 'iom.int', true),
('Defensoria Pública da União', 'DPU', 'DF', 'Brasília', 'https://www.dpu.def.br', 'dpu.def.br', true)
ON CONFLICT DO NOTHING;
