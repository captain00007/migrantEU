# Diretrizes de Segurança e Guardrails (DomainGuard & SafetyGuard)

1. **Proteção Contra SSRF e Scraping Não Autorizado:**
   - Nenhuma ferramenta do agente deve fazer requisições HTTP para domínios fora da `OFFICIAL_DOMAINS_WHITELIST` ou dos domínios oficiais registrados na tabela `institutions`.

2. **Sem Arquivos Temporários em Disco:**
   - O parsing de editais em PDF deve ocorrer 100% em memória através de buffers de bytes (`io.BytesIO`) e `pypdf`. Nunca salve arquivos na pasta `/tmp` ou no disco local.

3. **Proteção de Dados Pessoais (LGPD / PII):**
   - Documentos como CPFs e passaportes enviados por usuários no chat devem ser mascarados imediatamente por `SafetyGuard.sanitize_input()` antes de serem enviados aos provedores de LLM.
