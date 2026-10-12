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

def get_migranteu_agent(
    intent_key: str | None = None,
    provider: str | None = None,
    model: str | None = None
) -> AgentExecutor:
    """
    Constrói o agente LangChain integrado às ferramentas com o prompt especializado para a intenção do usuário.
    Evita prompts monolíticos genéricos, aplicando instruções direcionadas para cada tema.
    """
    tools = [
        check_cached_notices_tool,
        safe_web_search_tool,
        live_url_reader_tool,
        search_communities_tool
    ]
    llm = LLMFactory.get_llm(provider=provider, model=model, temperature=settings.AI_TEMPERATURE)

    # Seleciona o prompt específico da intenção
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
    Processa uma mensagem do usuário:
    1. Detecta a intenção semântica com um LLM ágil especializado (Google Gemini / OpenAI).
    2. Seleciona o prompt adequado e focado no tema específico.
    3. Executa o agente LangChain com fallback automático resiliente.
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

    # Passo 1: Detecta a intenção com LLM pequeno especializado
    intent_data = await IntentClassifier.detect_intent(
        prompt=sanitized_input,
        provider=active_provider,
        model=active_model
    )
    intent_key = intent_data.get("key", "geral_acolhimento")

    output_reply = ""

    # Passo 2: Executa o agente com o prompt especializado correspondente à intenção
    try:
        executor = get_migranteu_agent(
            intent_key=intent_key,
            provider=active_provider,
            model=active_model
        )
        response = await executor.ainvoke({
            'input': sanitized_input,
            'chat_history': formatted_history
        })
        output_reply = _extract_text(response.get('output', ''))
    except Exception as primary_err:
        print(f'[IA AVISO] Falha com {active_provider}/{active_model}: {primary_err}')
        
        # Fallback inteligente entre OpenAI e Gemini mantendo o mesmo prompt especializado
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
                    'input': sanitized_input,
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
