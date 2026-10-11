import re

class SafetyGuard:
    """
    Sanitiza consultas do usuário para prevenir injeções de prompt
    e mascarar dados pessoais sensíveis (PII).
    """
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        if not user_input:
            return ""
        # Remove caracteres de controle nulos
        cleaned = user_input.replace(chr(0), "")
        # Mascara números de CPF (padrão básico: 11 dígitos ou formatado)
        cleaned = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF PROTEGIDO]", cleaned)
        return cleaned.strip()
