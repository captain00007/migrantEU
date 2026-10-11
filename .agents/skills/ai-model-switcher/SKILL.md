---
name: ai-model-switcher
description: >-
  Procedimento para alternar dinamicamente os provedores de LLM (Google Gemini, OpenAI, Ollama)
  e modelos em tempo de execução via interface administrativa ou variáveis de ambiente.
---

# Skill: Alternância Dinâmica de Modelos de IA (migrantEU)

Esta skill orienta como testar e configurar os provedores de IA sem reiniciar o servidor FastAPI.

## Opções de Provedores Suportados

| Provedor | Identificador | Modelo LLM Típico | Embedding (768d) |
| :--- | :--- | :--- | :--- |
| **Google Gemini** (Padrão) | `google` ou `gemini` | `gemini-1.5-flash` | `models/text-embedding-004` |
| **OpenAI** | `openai` | `gpt-4o-mini` | `text-embedding-3-small` (768d) |
| **Ollama** (Local) | `ollama` ou `llama` | `llama3:8b` | `nomic-embed-text` |

## Como Alternar em Tempo de Execução

1. **Via Painel Administrativo:**
   - Acesse `/admin/dashboard` logado como administrador.
   - Na seção **🧠 Switch Ativo de Inteligência Artificial**, selecione o provedor desejado e informe o modelo.
   - Clique em **Salvar Configurações de IA**. A preferência é salva na tabela `system_settings` do Supabase e entra em vigor imediatamente para todas as novas mensagens do chat.

2. **Via Arquivo `.env` (Fallback Padrão):**
   - Altere as variáveis `AI_LLM_PROVIDER` e `AI_LLM_MODEL`.
