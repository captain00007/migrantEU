# migrantEU — Diretrizes do Projeto e Regras dos Agentes (AGENTS.md)

Este documento define as regras arquiteturais, diretrizes éticas e padrões de código obrigatórios para qualquer agente que atue no repositório **migrantEU**.

---

## 1. Visão do Produto e Missão
O **migrantEU** é uma plataforma comunitária, 100% gratuita, sem fricção de login para o usuário final (refugiados, solicitantes de refúgio e migrantes no Brasil), centralizando:
- Editais universitários (Cátedra Sérgio Vieira de Mello - CSVM, cotas e editais especiais).
- Cursos gratuitos de Português como Língua de Acolhimento (PLAC).
- Instituições parceiras de acolhimento social e jurídico (ACNUR, Cáritas, OIM, Defensoria Pública da União).
- Comunidades de apoio.

---

## 2. Stack Tecnológica Obrigatória (Monólito Python)
- **Backend & Servidor Web:** Python com **FastAPI**.
- **Frontend / Interface:** **Jinja2 + HTMX + Tailwind CSS via CDN**.
  - **ZERO dependências de Node.js/npm**.
  - PWA ativo com Service Worker (`app/static/sw.js`) e manifesto (`app/static/manifest.json`).
  - Interface reativa assíncrona com HTMX.
- **Banco de Dados & Vetores:** **100% Supabase** (PostgreSQL + extensão `pgvector` em 768 dimensões (padrão universal unificado entre Gemini, Ollama e OpenAI MRL)).
  - Nunca utilize bancos locais SQLite ou PostgreSQL separado quando em produção; utilize sempre o cliente oficial `supabase-py`.
- **Motor de IA & Orquestração:** **LangChain**.
- **Scheduler:** **APScheduler** integrado ao ciclo de vida `lifespan` do FastAPI.
- **Envio de E-mails:** **Resend** (API Python).

---

## 3. Regras de Inteligência Artificial e SOLID
1. **Separação Rígida de Responsabilidades:**
   - A pasta `app/ai/` deve manter separação estrita: `llm/` (Factory Pattern), `prompts/`, `guardrails/`, `loader/`, `cleaners/`, `splitter/`, `retrieval/`, `indexation/`, `tools/` e `agent.py`.
2. **Troca Dinâmica de Modelos:**
   - O sistema deve permitir trocar de provedor (`google`, `openai`, `ollama`) tanto pelo `.env` quanto pela tabela `system_settings` no painel administrativo sem reiniciar o servidor.
3. **Trava de Cache Obrigatória:**
   - Antes de qualquer busca externa na web, o agente DEVE consultar `check_cached_notices_tool`.
   - Se houver edital com `category`, `status = 'aprovado_vigente'` e `end_date >= CURRENT_DATE`, a busca na internet é **ESTRITAMENTE CONGELADA** e os dados do banco são retornados.
4. **Whitelist Estrita de Busca Web (Tavily):**
   - Buscas externas só podem acessar domínios permitidos: `.gov.br`, `.edu.br`, `acnur.org`, `iom.int`, `cbi.org.br`, `caritas.org.br`, `caritassp.org.br`, `dpu.def.br`.
5. **Human-in-the-Loop:**
   - Novos editais descobertos entram obrigatoriamente com `status = 'pendente_aprovacao'`.
   - Somente após aprovação do moderador no painel `/admin` o status muda para `aprovado_vigente` e os e-mails são disparados via Resend.
6. **Empatia e Multilíngue:**
   - Detectar o idioma do usuário (Espanhol, Francês, Crioulo Haitiano, Inglês, etc.) e responder na mesma língua.
   - NUNCA traduzir termos institucionais brasileiros (ex: CONARE, Polícia Federal, Cátedra Sérgio Vieira de Mello, UFPR, CPF, RNM).

---

## 4. Metodologia SDD e Registro Obrigatório de Modificações
1. **Regra Inviolável de Registro (CHANGELOG.md):**
   - **Para CADA feature, modificação ou refatoração realizada**, o agente DEVE registrar no arquivo `CHANGELOG.md`:
     - **O que foi feito** (descrição detalhada das mudanças técnicas e arquivos impactados).
     - **Por que foi feito** (justificativa de engenharia, requisito de negócio ou correção de bug).
2. **Especificar Antes de Codificar:**
   - Apresente sempre o plano estruturado antes de implementar novas funcionalidades.
3. **Validação de Compilação:**
   - Todo arquivo Python adicionado ou editado deve ser compilado e validado com `python3 -m py_compile` antes de concluir a resposta ao usuário.
