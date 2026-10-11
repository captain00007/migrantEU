---
name: manage-notices
description: >-
  Procedimento operacional para verificação de vigência, moderação de novos editais,
  aprovação Human-in-the-Loop e disparo de e-mails em lote via Resend no migrantEU.
---

# Skill: Gestão e Moderação de Editais (migrantEU)

Esta skill orienta o agente e operadores nos procedimentos de ingestão, moderação e publicação de editais.

## Fluxo Operacional

### 1. Verificação de Cache
- Sempre consulte `app/ai/retrieval/cache_checker.py` ou a tool `check_cached_notices_tool`.
- Se o edital retornar `status = 'aprovado_vigente'` e `end_date >= CURRENT_DATE`, informe ao usuário os dados do banco e encerre o fluxo sem acessar a internet.

### 2. Ingestão de Novo Edital
- Quando um novo edital for descoberto via `safe_web_search_tool` (Tavily):
  1. Insira na tabela `notices` do Supabase com `status = 'pendente_aprovacao'`.
  2. Gere o embedding com 768 dimensões via `NoticeIndexer`.
  3. Notifique no chat que a oportunidade foi encontrada e passará pela moderação oficial.

### 3. Aprovação Human-in-the-Loop
- No painel administrativo (`/admin/dashboard`):
  1. O moderador avalia o resumo, datas e link oficial.
  2. Ao clicar em **Aprovar & Disparar E-mails**, o endpoint `POST /admin/notices/{id}/approve` altera o status para `aprovado_vigente`.
  3. O `NoticeService` busca todos os assinantes em `subscribers` que possuem a categoria do edital em seu array `topics` e dispara alertas customizados via `EmailService` (Resend).
