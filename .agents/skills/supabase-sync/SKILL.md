---
name: supabase-sync
description: >-
  Procedimentos para sincronização de esquemas DDL, índices pgvector,
  execução de sementes (seeds) e testes da RPC match_notices no Supabase.
---

# Skill: Sincronização e Operação do Banco Supabase

Esta skill orienta sobre a infraestrutura de dados no Supabase para o migrantEU.

## Procedimento de Inicialização do Banco

1. Acesse o **SQL Editor** do projeto Supabase.
2. Execute o conteúdo de `sql/ddl.sql` para:
   - Habilitar `vector` e `uuid-ossp`.
   - Criar as tabelas `users`, `system_settings`, `institutions`, `notices`, `subscribers`.
   - O índice HNSW é opcional no MVP e deve ser ativado apenas sob alto volume de editais (busca flat padrão no início).
   - Criar a função RPC `match_notices`.
3. Execute o conteúdo de `sql/seeds.sql` para cadastrar o usuário administrador inicial e as instituições parceiras da CSVM.

## Teste da RPC de Busca Vetorial

Para testar a busca vetorial diretamente via Supabase client no backend:
```python
from app.core.database import SupabaseService

# Exemplo de chamada da RPC
result = await SupabaseService.rpc("match_notices", {
    "query_embedding": [...], # vetor de 768 posições
    "match_threshold": 0.60,
    "match_count": 5,
    "filter_category": "ensino_superior"
})
print(result.data)
```
