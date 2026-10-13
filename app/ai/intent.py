"""
Módulo de identificação de intenção do usuário via LLM para a plataforma migrantEU.
Utiliza um modelo de linguagem ágil e especializado para determinar o eixo temático da mensagem,
permitindo acionar o prompt adequado e especializado, com suporte a detecção de fora de escopo.
"""

from typing import Dict, Any, Optional
from app.core.config import settings
from app.ai.llm.factory import LLMFactory

INTENTS_MAP: Dict[str, Dict[str, Any]] = {
    "ensino_superior": {
        "key": "ensino_superior",
        "label": "🎓 Vagas Universitárias e Vestibulares",
        "badge_class": "bg-sky-50 text-sky-700 border-sky-200",
        "action_label": "Ver Editais de Graduação",
        "action_link": "/editais?categoria=ensino_superior"
    },
    "curso_portugues": {
        "key": "curso_portugues",
        "label": "🗣️ Cursos de Português (PLAC)",
        "badge_class": "bg-emerald-50 text-emerald-700 border-emerald-200",
        "action_label": "Ver Cursos de Idioma",
        "action_link": "/editais?categoria=curso_portugues"
    },
    "documentacao_refugio": {
        "key": "documentacao_refugio",
        "label": "📄 Documentação e Apoio Humanitário",
        "badge_class": "bg-amber-50 text-amber-700 border-amber-200",
        "action_label": "Portal do CONARE",
        "action_link": "https://www.gov.br/justica/pt-br/conare"
    },
    "comunidades": {
        "key": "comunidades",
        "label": "🤝 Comunidades e Redes de Acolhimento",
        "badge_class": "bg-indigo-50 text-indigo-700 border-indigo-200",
        "action_label": "Ver Associações",
        "action_link": "/comunidades"
    },
    "geral_acolhimento": {
        "key": "geral_acolhimento",
        "label": "💬 Orientação Geral e Acolhimento",
        "badge_class": "bg-slate-100 text-slate-700 border-slate-300",
        "action_label": "Explorar Oportunidades",
        "action_link": "/editais"
    },
    "fora_de_escopo": {
        "key": "fora_de_escopo",
        "label": "🛡️ Orientação sobre o Escopo migrantEU",
        "badge_class": "bg-slate-100 text-slate-600 border-slate-300",
        "action_label": "Ver Serviços da Plataforma",
        "action_link": "/editais"
    }
}

CLASSIFICATION_PROMPT_TEMPLATE = """Você é um classificador semântico de intenções da plataforma humanitária e educacional migrantEU.
Classifique a mensagem do usuário (que pode estar em qualquer idioma, como português, espanhol, francês, inglês, crioulo haitiano ou árabe) em EXATAMENTE UMA destas 6 opções:
- ensino_superior (vestibulares, faculdade, graduação, pós-graduação, mestrado, revalidação de diplomas, cotas acadêmicas)
- curso_portugues (cursos de português como língua de acolhimento - PLAC, aulas de língua, Celpe-Bras, aprender português)
- documentacao_refugio (solicitação de refúgio, asilo, CONARE, Polícia Federal, agendamento, CRNM, RNF, CPF, defensoria pública DPU, visto)
- comunidades (associações de imigrantes, coletivos por nacionalidade como venezuelanos, haitianos, afegãos, sírios, redes de apoio social)
- geral_acolhimento (saudações amigáveis como 'olá', agradecimentos, pedidos de ajuda geral voltados a migrantes ou dúvidas sobre o funcionamento da plataforma)
- fora_de_escopo (qualquer assunto alheio ao acolhimento e direitos de migrantes no Brasil, como esportes, futebol, atletas, celebridades, receitas, cultura pop, filmes, fofocas, piadas, programação geral ou conversas aleatórias descontextualizadas)

Mensagem do Usuário: "{message}"

Responda APENAS com a chave correspondente (ensino_superior, curso_portugues, documentacao_refugio, comunidades, geral_acolhimento ou fora_de_escopo) em minúsculas, sem pontuação, sem aspas e sem explicações adicionais."""


class IntentClassifier:
    """
    Classificador semântico de intenções alimentado por LLM.
    Remove heurísticas estáticas em favor da compreensão profunda de linguagem natural em múltiplos idiomas.
    """

    @classmethod
    async def detect_intent(
        cls,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa a classificação de intenção utilizando uma chamada rápida de LLM (temperatura 0.0).
        Inclui fallback automático transparente entre provedores para máxima disponibilidade.
        """
        clean_prompt = (prompt or "").strip()
        if not clean_prompt:
            return INTENTS_MAP["geral_acolhimento"]

        primary_provider = provider or settings.AI_LLM_PROVIDER
        primary_model = model or settings.AI_LLM_MODEL

        # Tenta classificar com o LLM primário
        try:
            llm = LLMFactory.get_llm(provider=primary_provider, model=primary_model, temperature=0.0)
            formatted_prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(message=clean_prompt[:500])
            response = await llm.ainvoke(formatted_prompt)
            raw_result = response.content if hasattr(response, 'content') else str(response)
            intent_key = cls._parse_key(raw_result)
            if intent_key in INTENTS_MAP:
                return INTENTS_MAP[intent_key]
        except Exception as primary_err:
            print(f"[INTENT LLM AVISO] Falha no classificador primário ({primary_provider}): {primary_err}")

        # Fallback transparente para o segundo provedor
        fallback_provider = 'openai' if (primary_provider or '').lower() in ['google', 'gemini'] else 'google'
        fallback_model = getattr(settings, 'OPENAI_LLM_MODEL', 'gpt-4o-mini') if fallback_provider == 'openai' else getattr(settings, 'GEMINI_LLM_MODEL', 'gemini-flash-latest')
        has_fb_key = bool(settings.OPENAI_API_KEY) if fallback_provider == 'openai' else bool(settings.GEMINI_API_KEY)

        if has_fb_key:
            try:
                fb_llm = LLMFactory.get_llm(provider=fallback_provider, model=fallback_model, temperature=0.0)
                formatted_prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(message=clean_prompt[:500])
                response = await fb_llm.ainvoke(formatted_prompt)
                raw_result = response.content if hasattr(response, 'content') else str(response)
                intent_key = cls._parse_key(raw_result)
                if intent_key in INTENTS_MAP:
                    return INTENTS_MAP[intent_key]
            except Exception as fb_err:
                print(f"[INTENT LLM ERRO] Falha também no fallback ({fallback_provider}): {fb_err}")

        # Se houver falha completa de rede em ambos os provedores, retorna acolhimento geral
        return INTENTS_MAP["geral_acolhimento"]

    @staticmethod
    def _parse_key(raw_text: Any) -> str:
        """Limpa e extrai a chave normalizada da resposta do LLM."""
        text = str(raw_text).strip().lower()
        for key in INTENTS_MAP.keys():
            if key in text:
                return key
        return "geral_acolhimento"