"""
Guardrail de escopo temático para o assistente da plataforma migrantEU.
Previne desvios de finalidade sem recorrer a listas estáticas hardcoded,
estabelecendo fronteiras claras de atuação em apoio a migrantes e refugiados.
"""

from typing import Optional

class ScopeGuard:
    """
    Guardrail que delimita as fronteiras temáticas do migrantEU:
    1. Ensino superior e revalidação de diplomas
    2. Cursos gratuitos de Português (PLAC)
    3. Documentação, refúgio e regularização (CONARE, PF, DPU)
    4. Redes de apoio comunitário e acolhimento social
    """

    SUPPORTED_INTENTS = {
        "ensino_superior",
        "curso_portugues",
        "documentacao_refugio",
        "comunidades",
        "geral_acolhimento"
    }

    OUT_OF_SCOPE_INTENT = "fora_de_escopo"

    @classmethod
    def is_out_of_scope(cls, intent_key: Optional[str]) -> bool:
        """Indica se a intenção classificada pelo modelo está fora do escopo da plataforma."""
        if not intent_key:
            return False
        return intent_key.strip().lower() == cls.OUT_OF_SCOPE_INTENT

    @classmethod
    def get_fallback_refusal(cls, language_code: str = "pt") -> str:
        """Mensagem de recusa e redirecionamento acolhedor no idioma do usuário."""
        code = (language_code or "pt").lower()[:2]
        messages = {
            "pt": (
                "Olá! Como assistente oficial da plataforma **migrantEU**, sou especializado exclusivamente em "
                "apoiar pessoas migrantes, refugiadas e solicitantes de refúgio no Brasil com:\n\n"
                "- 🎓 **Vagas Universitárias & Revalidação de Diplomas**\n"
                "- 🗣️ **Cursos Gratuitos de Português (PLAC)**\n"
                "- 📄 **Documentação & Refúgio (CONARE, Polícia Federal, CPF, DPU)**\n"
                "- 🤝 **Comunidades e Redes de Acolhimento Social**\n\n"
                "Por isso, não posso responder sobre temas fora deste escopo. "
                "Como posso ajudar você em relação à sua integração ou oportunidades no Brasil?"
            ),
            "es": (
                "¡Hola! Como asistente oficial de la plataforma **migrantEU**, estoy especializado exclusivamente en "
                "apoyar a personas migrantes y refugiadas en Brasil con:\n\n"
                "- 🎓 **Cupos Universitarios y Reválida de Títulos**\n"
                "- 🗣️ **Cursos Gratuitos de Portugués (PLAC)**\n"
                "- 📄 **Documentación y Refugio (CONARE, Policía Federal, CPF, DPU)**\n"
                "- 🤝 **Comunidades y Redes de Apoyo Social**\n\n"
                "Por ello, no puedo responder sobre temas fuera de este ámbito. "
                "¿Cómo puedo ayudarte en relación con tu integración u oportunidades en Brasil?"
            ),
            "fr": (
                "Bonjour ! En tant qu'assistant officiel de la plateforme **migrantEU**, je suis exclusivement dédié "
                "à l'accompagnement des personnes migrantes et réfugiées au Brésil pour :\n\n"
                "- 🎓 **Opportunités Universitaires & Équivalence de Diplômes**\n"
                "- 🗣️ **Cours Gratuits de Portugais (PLAC)**\n"
                "- 📄 **Régularisation & Asile (CONARE, Police Fédérale, CPF, DPU)**\n"
                "- 🤝 **Associations et Réseaux de Solidarité**\n\n"
                "Je ne peux donc pas répondre sur des sujets hors de ce cadre. "
                "Comment puis-je vous aider concernant votre intégration ou opportunités au Brésil ?"
            ),
            "en": (
                "Hello! As the official assistant for the **migrantEU** platform, I am exclusively specialized in "
                "supporting migrants and refugees in Brazil with:\n\n"
                "- 🎓 **University Opportunities & Diploma Recognition**\n"
                "- 🗣️ **Free Portuguese Courses (PLAC)**\n"
                "- 📄 **Documentation & Asylum (CONARE, Federal Police, CPF, DPU)**\n"
                "- 🤝 **Community Support Networks and Associations**\n\n"
                "Therefore, I cannot discuss topics outside this scope. "
                "How can I assist you with your integration or opportunities in Brazil?"
            )
        }
        return messages.get(code, messages["pt"])
