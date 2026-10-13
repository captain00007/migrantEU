from typing import List, Dict, Any, Tuple, Union
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from app.core.config import settings
from app.ai.prompts.specialized import get_prompt_for_intent, PROMPT_GERAL_ACOLHIMENTO
from app.ai.intent import IntentClassifier, INTENTS_MAP
from app.ai.llm.factory import LLMFactory
from app.ai.tools.check_cache import check_cached_notices_tool
from app.ai.tools.safe_search import safe_web_search_tool
from app.ai.tools.live_reader import live_url_reader_tool
from app.ai.tools.check_communities import search_communities_tool
from app.ai.guardrails.safety_guard import SafetyGuard
from app.ai.guardrails.scope_guard import ScopeGuard
from app.ai.guardrails.context_shield import ContextShield

def _extract_text(output: Any) -> str:
    """Extrai texto limpo independentemente do formato retornado pelo LLM (string ou blocos)."""
    if isinstance(output, list):
        parts = []
        for item in output:
            if isinstance(item, dict) and 'text' in item:
                parts.append(str(item['text']))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()
    elif isinstance(output, dict) and 'text' in output:
        return str(output['text']).strip()
    elif isinstance(output, str):
        return output.strip()
    return str(output).strip()

def detect_user_language(text: str) -> str:
    """Identifica o idioma predominante do texto para recusas e acolhimentos empáticos."""
    lowered = (text or "").lower()
    if any(w in lowered for w in ["hola", "gracias", "por favor", "¿", "necesito", "ayuda", "universidad", "refugio", "estudiar"]):
        return "es"
    if any(w in lowered for w in ["bonjour", "merci", "s'il vous plaît", "comment", "je ", "aide", "université", "asile"]):
        return "fr"
    if any(w in lowered for w in ["hello", "hi ", "thanks", "please", "help", "university", "asylum", "refugee", "how to"]):
        return "en"
    return "pt"

def get_tools_for_intent(intent_key: str | None = None) -> list:
    """
    Retorna apenas as ferramentas necessárias para a intenção detectada,
    evitando poluir a assinatura do modelo com chamadas irrelevantes.
    """
    key = (intent_key or "").strip().lower()
    if key in ["ensino_superior", "curso_portugues"]:
        # Foco em consulta de editais e busca oficial
        return [
            check_cached_notices_tool,
            safe_web_search_tool,
            live_url_reader_tool
        ]
    elif key == "comunidades":
        # Foco em consulta de associações comunitárias
        return [
            search_communities_tool,
            safe_web_search_tool,
            live_url_reader_tool
        ]
    elif key == "documentacao_refugio":
        # Foco em busca oficial governamental (Sisconare/PF/DPU)
        return [
            safe_web_search_tool,
            live_url_reader_tool
        ]
    else:
        # Orientação geral de acolhimento: disponibiliza o leque completo
        return [
            check_cached_notices_tool,
            search_communities_tool,
            safe_web_search_tool,
            live_url_reader_tool
        ]

def get_migranteu_agent(
    intent_key: str | None = None,
    provider: str | None = None,
    model: str | None = None
) -> AgentExecutor:
    """
    Constrói o agente LangChain integrado estritamente com as ferramentas e com o
    prompt específico da intenção do usuário, evitando prompts monolíticos.
    """
    tools = get_tools_for_intent(intent_key)
    llm = LLMFactory.get_llm(provider=provider, model=model, temperature=settings.AI_TEMPERATURE)

    # Carrega exclusivamente o prompt do domínio solicitado (sem empilhar todos os eixos)
    system_prompt = get_prompt_for_intent(intent_key)

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=settings.AI_AGENT_MAX_ITERATIONS,
        handle_parsing_errors=True
    )
    return executor

async def process_chat_message(
    user_input: str,
    chat_history: List[Dict[str, str]] | None = None,
    provider: str | None = None,
    model: str | None = None,
    return_intent: bool = False
) -> Union[str, Tuple[str, Dict[str, Any]]]:
    """
    Processa a mensagem do usuário com pipeline em duas etapas:
    1. O primeiro LLM (rápido) identifica a intenção semântica.
    2. Avaliação de continuidade:
       - Se for fora de escopo (ou tema sem ameaça de acolhimento), encerra imediatamente
         com recusa acolhedora no idioma do usuário, economizando chamadas e ferramentas.
    3. Se dentro do escopo:
       - Encapsula a pergunta do usuário com ContextShield (XML/CDATA) para separar dados de instruções.
       - Seleciona o prompt específico daquele tema (ex: ensino superior OU comunidades).
       - Dispara o agente LangChain com ferramentas específicas.
    """
    sanitized_input = SafetyGuard.sanitize_input(user_input)
    formatted_history: List[BaseMessage] = []
    if chat_history:
        for msg in chat_history:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role in ['user', 'human']:
                formatted_history.append(HumanMessage(content=content))
            elif role in ['assistant', 'bot', 'ai']:
                formatted_history.append(AIMessage(content=content))

    active_provider = provider or settings.AI_LLM_PROVIDER
    active_model = model or settings.AI_LLM_MODEL

    # Etapa 1: Primeiro LLM ágil descobre a intenção do usuário
    intent_data = await IntentClassifier.detect_intent(
        prompt=sanitized_input,
        provider=active_provider,
        model=active_model
    )
    intent_key = intent_data.get("key", "geral_acolhimento")

    # Etapa 2: Verifica se precisa continuar
    # Se a intenção for fora de escopo, não é necessário continuar para o segundo LLM com ferramentas
    if ScopeGuard.is_out_of_scope(intent_key):
        user_lang = detect_user_language(sanitized_input)
        refusal_msg = ScopeGuard.get_fallback_refusal(user_lang)
        if return_intent:
            return refusal_msg, intent_data
        return refusal_msg

    output_reply = ""

    # Etapa 3: Continua para o segundo LLM com ContextShield (Data vs. Instructions)
    shielded_input = ContextShield.format_user_query(sanitized_input)

    try:
        executor = get_migranteu_agent(
            intent_key=intent_key,
            provider=active_provider,
            model=active_model
        )
        response = await executor.ainvoke({
            'input': shielded_input,
            'chat_history': formatted_history
        })
        output_reply = _extract_text(response.get('output', ''))
    except Exception as primary_err:
        print(f'[IA AVISO] Falha com {active_provider}/{active_model}: {primary_err}')
        
        # Fallback inteligente entre OpenAI e Gemini mantendo o mesmo prompt modular
        fallback_provider = 'openai' if (active_provider or '').lower() in ['google', 'gemini'] else 'google'
        fallback_model = getattr(settings, 'OPENAI_LLM_MODEL', 'gpt-4o-mini') if fallback_provider == 'openai' else getattr(settings, 'GEMINI_LLM_MODEL', 'gemini-flash-latest')
        has_key = bool(settings.OPENAI_API_KEY) if fallback_provider == 'openai' else bool(settings.GEMINI_API_KEY)

        if has_key:
            try:
                print(f'[IA FALLBACK] Ativando fallback para {fallback_provider}/{fallback_model} (intent: {intent_key})...')
                fallback_executor = get_migranteu_agent(
                    intent_key=intent_key,
                    provider=fallback_provider,
                    model=fallback_model
                )
                response = await fallback_executor.ainvoke({
                    'input': shielded_input,
                    'chat_history': formatted_history
                })
                output_reply = _extract_text(response.get('output', ''))
            except Exception as fb_err:
                print(f'[IA ERRO] Falha também no fallback ({fallback_provider}): {fb_err}')

    if not output_reply:
        output_reply = 'Desculpe, ocorreu uma instabilidade momentânea na conexão com o assistente inteligente. Por favor, tente novamente em instantes ou consulte a seção Editais & Cursos para conferir as vagas cadastradas.'

    if return_intent:
        return output_reply, intent_data
    return output_reply

async def process_chat_message_with_intent(
    user_input: str,
    chat_history: List[Dict[str, str]] | None = None,
    provider: str | None = None,
    model: str | None = None
) -> Tuple[str, Dict[str, Any]]:
    """Função de conveniência que retorna tanto a resposta quanto os metadados da intenção detectada."""
    result = await process_chat_message(
        user_input=user_input,
        chat_history=chat_history,
        provider=provider,
        model=model,
        return_intent=True
    )
    if isinstance(result, tuple):
        return result
    return result, INTENTS_MAP["geral_acolhimento"]
