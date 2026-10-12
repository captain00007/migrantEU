from typing import List, Dict, Any, AsyncGenerator
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
except ImportError:
    from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from app.core.config import settings
from app.ai.prompts.system import SYSTEM_PROMPT
from app.ai.llm.factory import LLMFactory
from app.ai.tools.check_cache import check_cached_notices_tool
from app.ai.tools.safe_search import safe_web_search_tool
from app.ai.tools.live_reader import live_url_reader_tool
from app.ai.guardrails.safety_guard import SafetyGuard

def get_migranteu_agent(provider: str | None = None, model: str | None = None) -> AgentExecutor:
    """
    Constrói o agente LangChain integrado às ferramentas com resolução dinâmica de modelo a partir do settings/.env.
    """
    tools = [check_cached_notices_tool, safe_web_search_tool, live_url_reader_tool]
    llm = LLMFactory.get_llm(provider=provider, model=model, temperature=settings.AI_TEMPERATURE)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
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
    model: str | None = None
) -> str:
    """
    Processa uma mensagem do usuário pelo agente, formatando histórico e aplicando guardrails.
    """
    sanitized_input = SafetyGuard.sanitize_input(user_input)
    formatted_history: List[BaseMessage] = []
    if chat_history:
        for msg in chat_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role in ["user", "human"]:
                formatted_history.append(HumanMessage(content=content))
            elif role in ["assistant", "bot", "ai"]:
                formatted_history.append(AIMessage(content=content))

    executor = get_migranteu_agent(provider=provider, model=model)
    response = await executor.ainvoke({
        "input": sanitized_input,
        "chat_history": formatted_history
    })
    return response.get("output", "Desculpe, ocorreu um erro ao processar sua pergunta.")
