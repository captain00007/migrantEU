"""
Sistema de prompts do migrantEU.
Para prompts especializados por intenção, consulte `specialized.py`.
"""

from app.ai.prompts.specialized import (
    PROMPT_GERAL_ACOLHIMENTO,
    PROMPT_ENSINO_SUPERIOR,
    PROMPT_CURSO_PORTUGUES,
    PROMPT_DOCUMENTACAO_REFUGIO,
    PROMPT_COMUNIDADES,
    PROMPTS_BY_INTENT,
    get_prompt_for_intent,
)

# Compatibilidade retroativa para módulos que importam SYSTEM_PROMPT diretamente
SYSTEM_PROMPT = PROMPT_GERAL_ACOLHIMENTO

__all__ = [
    "SYSTEM_PROMPT",
    "PROMPT_GERAL_ACOLHIMENTO",
    "PROMPT_ENSINO_SUPERIOR",
    "PROMPT_CURSO_PORTUGUES",
    "PROMPT_DOCUMENTACAO_REFUGIO",
    "PROMPT_COMUNIDADES",
    "PROMPTS_BY_INTENT",
    "get_prompt_for_intent",
]
