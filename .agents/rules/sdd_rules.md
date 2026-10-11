# Regras de Desenvolvimento Dirigido por Especificações (SDD)

Ao atuar no **migrantEU**, o agente deve aderir às seguintes práticas:

1. **Registro Obrigatório de Modificações (O que foi feito & Por que):**
   - Para qualquer feature, alteração de configuração, schema de dados ou código, registre no `CHANGELOG.md`:
     - **O que foi feito:** Itens modificados e arquivos impactados.
     - **Por que foi feito:** Motivação técnica, regra de negócio ou benefício arquitetural.

2. **Especificar Antes de Codificar:**
   - Apresente o plano estruturado antes de implementar novas funcionalidades.
   - Verifique os modelos de dados e contratos de endpoints antes de criar novas rotas.

3. **Imutabilidade das Regras de Negócio:**
   - Uma instituição possui 1:N editais (`notices`).
   - O campo `end_date` governa o congelamento ou liberação de buscas na web.
   - Assinantes em `subscribers` recebem alertas com base nos tópicos selecionados (`topics`).

4. **Verificação de Compilação:**
   - Todo arquivo Python adicionado ou editado deve ser compilado e validado via `python3 -m py_compile` antes de concluir a tarefa.
