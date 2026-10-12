-- ============================================================================
-- migrantEU - Seeds Iniciais (Categorias, Instituições e Configuração de IA)
-- Administradores: Criar diretamente no Supabase em Authentication -> Users
-- ============================================================================

-- 1. Configuração inicial de IA em system_settings
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

-- 2. Categorias Oficiais Dinâmicas de Oportunidades
INSERT INTO categories (slug, name, description, badge_color, is_active) VALUES
('ensino_superior', 'Ensino Superior (Graduação)', 'Vestibulares específicos, cotas e vagas suplementares para migrantes e refugiados', 'blue', true),
('curso_portugues', 'Cursos de Português (PLAC)', 'Português como Língua de Acolhimento em universidades parceiras', 'emerald', true),
('pos_graduacao', 'Pós-Graduação', 'Mestrado, Doutorado e especializações com vagas afirmativas', 'purple', true),
('acolhimento_social', 'Acolhimento e Apoio Jurídico', 'Orientação jurídica, regularização documental e assistência social', 'amber', true),
('revalidacao_diploma', 'Revalidação de Diplomas', 'Processos de reconhecimento e revalidação simplificada de diplomas estrangeiros', 'indigo', true)
ON CONFLICT (slug) DO NOTHING;

-- 3. Instituições Oficiais Parceiras (Universidades CSVM e Entidades de Acolhimento)
INSERT INTO institutions (name, sigla, uf, city, website_url, official_domain, is_active) VALUES
-- Sul
('Universidade Federal do Paraná', 'UFPR', 'PR', 'Curitiba', 'https://www.ufpr.br', 'ufpr.br', true),
('Univ. Fed. da Integração Latino-Americana', 'UNILA', 'PR', 'Foz do Iguaçu', 'https://www.unila.edu.br', 'unila.edu.br', true),
('Universidade Federal de Santa Catarina', 'UFSC', 'SC', 'Florianópolis', 'https://www.ufsc.br', 'ufsc.br', true),
('Univ. Federal da Fronteira Sul', 'UFFS', 'SC', 'Chapecó', 'https://www.uffs.edu.br', 'uffs.edu.br', true),
('Universidade Federal do Rio Grande do Sul', 'UFRGS', 'RS', 'Porto Alegre', 'https://www.ufrgs.br', 'ufrgs.br', true),
('Universidade Federal de Santa Maria', 'UFSM', 'RS', 'Santa Maria', 'https://www.ufsm.br', 'ufsm.br', true),
('Univ. do Vale do Rio dos Sinos', 'UNISINOS', 'RS', 'São Leopoldo', 'https://www.unisinos.br', 'unisinos.br', true),

-- Sudeste
('Universidade de São Paulo', 'USP', 'SP', 'São Paulo', 'https://www.usp.br', 'usp.br', true),
('Universidade Estadual de Campinas', 'UNICAMP', 'SP', 'Campinas', 'https://www.unicamp.br', 'unicamp.br', true),
('Universidade Federal de São Paulo', 'UNIFESP', 'SP', 'São Paulo', 'https://www.unifesp.br', 'unifesp.br', true),
('Universidade Federal de São Carlos', 'UFSCar', 'SP', 'São Carlos', 'https://www.ufscar.br', 'ufscar.br', true),
('Universidade Federal do ABC', 'UFABC', 'SP', 'Santo André', 'https://www.ufabc.edu.br', 'ufabc.edu.br', true),
('Universidade Federal do Rio de Janeiro', 'UFRJ', 'RJ', 'Rio de Janeiro', 'https://www.ufrj.br', 'ufrj.br', true),
('Universidade Federal Fluminense', 'UFF', 'RJ', 'Niterói', 'https://www.uff.br', 'uff.br', true),
('Univ. do Estado do Rio de Janeiro', 'UERJ', 'RJ', 'Rio de Janeiro', 'https://www.uerj.br', 'uerj.br', true),
('Universidade Federal de Minas Gerais', 'UFMG', 'MG', 'Belo Horizonte', 'https://www.ufmg.br', 'ufmg.br', true),
('Universidade Federal de Uberlândia', 'UFU', 'MG', 'Uberlândia', 'https://www.ufu.br', 'ufu.br', true),
('Universidade Federal do Espírito Santo', 'UFES', 'ES', 'Vitória', 'https://www.ufes.br', 'ufes.br', true),

-- Centro-Oeste
('Universidade de Brasília', 'UnB', 'DF', 'Brasília', 'https://www.unb.br', 'unb.br', true),
('Universidade Federal de Goiás', 'UFG', 'GO', 'Goiânia', 'https://www.ufg.br', 'ufg.br', true),
('Univ. Federal de Mato Grosso do Sul', 'UFMS', 'MS', 'Campo Grande', 'https://www.ufms.br', 'ufms.br', true),

-- Nordeste
('Universidade Federal da Bahia', 'UFBA', 'BA', 'Salvador', 'https://www.ufba.br', 'ufba.br', true),
('Universidade Federal da Paraíba', 'UFPB', 'PB', 'João Pessoa', 'https://www.ufpb.br', 'ufpb.br', true),
('Univ. Estadual da Paraíba', 'UEPB', 'PB', 'Campina Grande', 'https://www.uepb.edu.br', 'uepb.edu.br', true),
('Universidade Federal de Pernambuco', 'UFPE', 'PE', 'Recife', 'https://www.ufpe.br', 'ufpe.br', true),
('Universidade Federal do Ceará', 'UFC', 'CE', 'Fortaleza', 'https://www.ufc.br', 'ufc.br', true),
('Univ. Estadual do Ceará', 'UECE', 'CE', 'Fortaleza', 'https://www.uece.br', 'uece.br', true),

-- Norte
('Universidade Federal do Amazonas', 'UFAM', 'AM', 'Manaus', 'https://www.ufam.edu.br', 'ufam.edu.br', true),
('Universidade Federal de Roraima', 'UFRR', 'RR', 'Boa Vista', 'https://www.ufrr.br', 'ufrr.br', true),
('Universidade Federal do Pará', 'UFPA', 'PA', 'Belém', 'https://www.ufpa.br', 'ufpa.br', true),
('Universidade Federal do Acre', 'UFAC', 'AC', 'Rio Branco', 'https://www.ufac.br', 'ufac.br', true),

-- Agências e Órgãos Humanitários
('Cáritas Arquidiocesana de São Paulo', 'Cáritas SP', 'SP', 'São Paulo', 'https://caritassp.org.br', 'caritassp.org.br', true),
('Alto Comissariado das Nações Unidas para Refugiados', 'ACNUR Brasil', 'DF', 'Brasília', 'https://www.acnur.org/portugues', 'acnur.org', true),
('Organização Internacional para as Migrações', 'OIM Brasil', 'DF', 'Brasília', 'https://brazil.iom.int', 'iom.int', true),
('Defensoria Pública da União', 'DPU', 'DF', 'Brasília', 'https://www.dpu.def.br', 'dpu.def.br', true)
ON CONFLICT DO NOTHING;
