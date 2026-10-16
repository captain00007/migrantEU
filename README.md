# 🌍 migrantEU — Plataforma de Oportunidades & Acolhimento

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-pgvector_768d-3ECF8E.svg)](https://supabase.com/)
[![LangChain](https://img.shields.io/badge/LangChain-SOLID_Architecture-1C3C3C.svg)](https://www.langchain.com/)
[![HTMX](https://img.shields.io/badge/Frontend-HTMX_+_Jinja2-336699.svg)](https://htmx.org/)
[![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind_CDN-38B2AC.svg)](https://tailwindcss.com/)
[![PWA Ready](https://img.shields.io/badge/PWA-Offline_First-5A0FC8.svg)](https://web.dev/progressive-web-apps/)
[![Tests](https://img.shields.io/badge/Tests-Pytest_100%25_Passing-brightgreen.svg)](https://docs.pytest.org/)

O **migrantEU** é uma plataforma voltada a migrantes, solicitantes de refúgio e refugiados no Brasil. O sistema centraliza oportunidades educacionais e redes de acolhimento social com zero fricção de acesso (sem login para o usuário final) e eficiência máxima de dados.

---

## 🎯 Pilares e Funcionalidades

1. **Oportunidades em Universidades Públicas:** Editais de vagas especiais, cotas para refugiados em instituições como UFPR, UNILA. UFFS, etc.
2. **Cursos Gratuitos de Português:** Localizador e alertas de cursos de **Português como Língua de Acolhimento (PLAC)**.
3. **Rede de Apoio Humanitário** Conexão com órgãos oficiais e entidades de acolhimento.
4. **Assistente Virtual Multilíngue com IA:** Agente conversacional que detecta a língua do migrante (Espanhol, Francês, Crioulo Haitiano, Inglês, etc.) e responde empaticamente com base em fontes oficiais.
5. **Alertas em Tempo Real por E-mail:** Inscrição rápida por tópicos de interesse com notificações automáticas via **Resend**.
6. **Moderação Human-in-the-Loop:** Painel administrativo protegido pelo para validação prévia de novos editais descobertos na internet antes do disparo aos usuários.

---

## 🏗️ Arquitetura da Stack (Monólito Python)

O projeto foi construído sob a metodologia **SDD (Spec-Driven Development)**, sem dependências de Node.js/npm:

- **Backend & Servidor Web:** **Python com FastAPI**.
- **Interface & Reatividade:** **Jinja2 + HTMX + Tailwind CSS (via CDN)**.
- **PWA (Progressive Web App):** Manifesto e Service Worker (`sw.js`) para instalação em celulares e suporte a cache offline.
- **Banco de Dados & Busca Semântica:** **100% Supabase** (PostgreSQL com extensão `pgvector` unificada em **768 dimensões**).
- **Conexão com o Banco:** API RESTful / HTTPS sobre PostgREST via `supabase-py` assíncrono (sem conexão TCP pesada).
- **Motor de Inteligência Artificial:** **LangChain** estruturado sob princípios **SOLID**:
  - `llm/`: Factory Pattern com troca dinâmica de provedores em tempo de execução (**Google Gemini**, **OpenAI**, **Ollama**).
  - `guardrails/`: Whitelist estrita de domínios governamentais e acadêmicos (`DomainGuard`) e mascaramento de dados sensíveis (`SafetyGuard`).
  - `retrieval/`: Trava inteligente de cache (`CacheChecker`), impedindo buscas externas na web caso haja edital vigente no banco.
  - `loader/`: Extração de texto de editais em PDF.
  - `tools/`: `check_cached_notices_tool`, `safe_web_search_tool` (Tavily restrito) e `live_url_reader_tool`.
- **Autenticação Administrativa:** **Supabase Auth nativo**.
- **Envio de E-mails:** **Resend API**.
- **Agendador de Tarefas:** **APScheduler** para expiração diária de editais vencidos.

---

## 📂 Estrutura do Repositório

```text
migrantEU/
├── AGENTS.md                     # Regras globais de governança dos agentes IA
├── CHANGELOG.md                  # Registro formal de features e justificativas técnicas
├── pytest.ini                    # Configuração de testes automatizados
├── requirements.txt              # Dependências Python pinadas
├── .env.example                  # Modelo de variáveis de ambiente
├── .agents/                      # Customizações do Antigravity IDE
│   ├── rules/                    # Regras SDD, SOLID e Guardrails de Segurança
│   └── skills/                   # Runbooks de moderação, troca de IA e sincronização Supabase
├── sql/
│   ├── ddl.sql                   # Schema DDL (pgvector 768d, índices, RPC match_notices)
│   └── seeds.sql                 # Universidades parceiras e configurações iniciais
├── app/
│   ├── main.py                   # Ponto de entrada FastAPI com ciclo de vida (lifespan)
│   ├── core/                     # Configurações, segurança e cliente Supabase REST
│   ├── models/                   # Schemas Pydantic tipados
│   ├── services/                 # NoticeService, EmailService (Resend) e Scheduler
│   ├── ai/                       # Núcleo modular de IA (SOLID)
│   │   ├── llm/                  # Factory de modelos e provedores (Gemini, OpenAI, Ollama)
│   │   ├── prompts/              # Prompts empáticos multilíngues
│   │   ├── guardrails/           # Whitelist de domínios e proteção de CPF
│   │   ├── loader/               # Loaders web e PDF in-memory
│   │   ├── cleaners/             # Higienização de texto
│   │   ├── splitter/             # Chunking semântico
│   │   ├── retrieval/            # Verificador de vigência no Supabase
│   │   ├── indexation/           # Indexador de vetores 768d
│   │   ├── tools/                # Tools do LangChain com trava de cache
│   │   └── agent.py              # Agente conversacional Tool-Calling
│   ├── routers/                  # web.py (Jinja2), api.py (HTMX) e admin.py (Supabase Auth)
│   ├── templates/                # Templates Jinja2 e componentes parciais HTMX
│   └── static/                   # CSS customizado, PWA Service Worker, manifest e ícones
└── tests/                        # Suíte de testes com Pytest
    ├── conftest.py               # Fixtures compartilhadas e mocks do Supabase
    ├── unit/                     # Testes unitários (Guardrails, Cleaners, LLM, Security)
    ├── integration/              # Testes de integração (NoticeService, CacheTools, Resend)
    └── e2e/                      # Testes ponta a ponta (Web, HTMX, Login Admin)
```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o Repositório e Criar o Ambiente Virtual

```bash
cd migrantEU
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar as Variáveis de Ambiente

Copie o modelo `.env.example` para `.env`:
```bash
cp .env.example .env
```

Preencha os campos essenciais:
- `SUPABASE_URL`: URL do seu projeto no Supabase (`https://seu-projeto.supabase.co`).
- `SUPABASE_SERVICE_ROLE_KEY`: Chave de serviço secreta do Supabase (para backend).
- `SUPABASE_ANON_KEY`: Chave anônima pública do Supabase (para autenticação).
- `GEMINI_API_KEY`: Chave gratuita obtida no [Google AI Studio](https://aistudio.google.com/).
- `TAVILY_API_KEY`: Chave da API [Tavily](https://tavily.com/) para buscas web oficiais.
- `RESEND_API_KEY`: *(Opcional)* Chave do [Resend](https://resend.com/) para disparos reais de e-mail (em desenvolvimento, o envio é simulado no terminal).

### 3. Executar os Scripts SQL no Supabase

No painel do seu Supabase, abra o **SQL Editor** e execute na ordem:
1. O conteúdo de [`sql/ddl.sql`](sql/ddl.sql) (habilita `vector`, cria tabelas, índices e a função RPC `match_notices`).
2. O conteúdo de [`sql/seeds.sql`](sql/seeds.sql) (cadastra as universidades e dados de apoio iniciais).

### 4. Criar o Primeiro Usuário Administrador no Supabase Auth

1. Acesse o Supabase Dashboard ➔ **Authentication** ➔ **Users**.
2. Clique em **"Add user"** ➔ **"Create user"**.
3. Defina o e-mail (ex: `admin@migranteu.org`), senha e marque **"Auto Confirm User?"**.
4. *(Opcional)* Em **User Metadata**, adicione:
   ```json
   { "role": "admin", "full_name": "Administrador Principal" }
   ```

### 5. Iniciar o Servidor FastAPI

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse no navegador:
- 🌐 **Página Inicial:** `http://localhost:8000/`
- 📚 **Catálogo de Editais (com filtros HTMX):** `http://localhost:8000/editais`
- 💬 **Assistente Virtual Multilíngue:** `http://localhost:8000/chat`
- 🔒 **Painel Administrativo:** `http://localhost:8000/admin/dashboard` (Login via Supabase Auth em `/admin/login`)

---

## 🧪 Suíte de Testes Automatizados (Pytest)

A aplicação conta com cobertura completa nas três camadas de testes:

```bash
# Executar todos os testes (35 testes automatizados)
pytest -v

# Executar apenas testes unitários
pytest -m unit -v

# Executar apenas testes de integração
pytest -m integration -v

# Executar apenas testes de ponta a ponta (E2E)
pytest -m e2e -v
```

---

## 🛡️ Segurança & Privacidade

- **Proteção de Dados Pessoais:** O guardrail `SafetyGuard` mascara automaticamente números de CPF e documentos de identidade antes de qualquer envio aos modelos de linguagem.
- **Whitelist Rígida de Domínios:** Nenhuma ferramenta de busca ou leitura externa acessa URLs fora de portais governamentais (`.gov.br`), acadêmicos (`.edu.br`) e agências humanitárias oficiais (ACNUR, OIM).
- **Parsing In-Memory:** Documentos PDF nunca são armazenados no disco rígido do servidor, garantindo privacidade e custo zero de armazenamento efêmero.

---

## 📄 Compromisso 

Desenvolvido para apoiar a reconstrução de vidas, o acesso à educação superior e o acolhimento digno de pessoas em situação de refúgio e migração no Brasil.
