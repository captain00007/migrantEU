# Regras de Arquitetura de IA (SOLID & Factory Pattern)

Para o diretório `app/ai/`, as seguintes restrições de arquitetura devem ser estritamente preservadas:

1. **Single Responsibility Principle (SRP):**
   - `loader/`: Apenas extrai dados brutos (web ou PDF em memória).
   - `cleaners/`: Apenas sanitiza e remove ruídos de formatação/HTML.
   - `splitter/`: Apenas divide texto em pedaços semânticos.
   - `guardrails/`: Apenas valida restrições de segurança e domínios.
   - `llm/factory.py`: Apenas instancia modelos `BaseChatModel` e `Embeddings`.
   - `retrieval/`: Apenas consulta e recupera dados do cache ou do pgvector.

2. **Open/Closed Principle (OCP):**
   - Para adicionar um novo provedor de IA (ex: Anthropic, Mistral), crie uma nova classe em `app/ai/llm/providers/` implementando `BaseLLMProvider` sem alterar o código do agente.

3. **Dependency Inversion Principle (DIP):**
   - O agente conversacional `agent.py` depende apenas de interfaces abstratas do LangChain (`BaseChatModel`, `Embeddings`, `BaseTool`), nunca de clientes proprietários diretamente.
