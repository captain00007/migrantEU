import re
from typing import Tuple, Optional

class SafetyGuard:
    """
    Sanitiza consultas do usuário para prevenir injeções de prompt,
    mascarar dados pessoais sensíveis (PII) e bloquear violações de segurança.
    """

    # Padrões de Prompt Injection, Jailbreak e tentativas de subversão do modelo
    PROMPT_INJECTION_PATTERNS = [
        r"(?i)\bignore\b.*?\b(instructions|instruç(ões|oes)|regras|diretrizes)\b",
        r"(?i)\bforget\b.*?\binstructions\b",
        r"(?i)\bdesconsidere\b.*?\b(instruç(ões|oes)|regras|diretrizes)\b",
        r"(?i)\besqueça\b.*?\b(instruç(ões|oes)|regras|diretrizes)\b",
        r"(?i)\b(dan\s+mode|jailbreak|developer\s+mode\s+output|modo\s+desenvolvedor)\b",
        r"(?i)\b(bypass|burlar?)\b.*?\b(security|safeguards?|filters?|safety|guardrails?|regras?|filtros?|segurança)\b",
        r"(?i)\b(reveal|show|print|leak|display)\b.*?\b(system\s+prompt|initial\s+prompt|hidden\s+instructions)\b",
        r"(?i)\b(mostre|revele|exiba|imprima)\b.*?\bprompt\s+(de\s+sistema|original|inicial)\b",
        r"(?i)\b(reveal|show|leak|mostre|revele|exiba)\b.*?\b(api[\s_-]?key|secret[\s_-]?key|chaves?(\s+de\s+api)?|token|password|credentials|credenciais|senhas?)\b",
    ]

    # Padrões de código e scripts potencialmente maliciosos (XSS, SQLi destrutivo, comandos shell)
    MALICIOUS_CODE_PATTERNS = [
        r"(?i)<\s*script\b[^>]*>",
        r"(?i)javascript:\s*",
        r"(?i)onload\s*=",
        r"(?i)onerror\s*=",
        r"(?i)<\s*iframe\b[^>]*>",
        r"(?i);\s*(drop|delete|truncate|alter)\s+table\b",
        r"(?i)\bunion\s+all\s+select\b|\bunion\s+select\b",
        r"(?i);\s*(rm\s+-rf|sudo\s+|curl\s+.*\|\s*bash|wget\s+.*\|\s*bash)\b",
    ]

    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        """
        Sanitiza a entrada removendo caracteres nulos e mascarando números de CPF
        para conformidade com a LGPD.
        """
        if not user_input:
            return ""
        # Remove caracteres de controle nulos
        cleaned = user_input.replace(chr(0), "")
        # Mascara números de CPF (padrão básico: 11 dígitos ou formatado)
        cleaned = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF PROTEGIDO]", cleaned)
        return cleaned.strip()

    @classmethod
    def check_safety(cls, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Avalia se a consulta do usuário viola alguma regra de segurança da plataforma:
        - Tentativas de injeção de prompt ou quebra de diretrizes (jailbreak)
        - Inserção de scripts e injeções de código executável
        
        Retorna:
            (True, None) se a mensagem estiver em conformidade com as regras de segurança.
            (False, "motivo_da_violacao") caso seja detectada violação.
        """
        if not user_input or not user_input.strip():
            return True, None

        cleaned = cls.sanitize_input(user_input)

        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, cleaned):
                return False, "prompt_injection"

        for pattern in cls.MALICIOUS_CODE_PATTERNS:
            if re.search(pattern, cleaned):
                return False, "malicious_code"

        return True, None

    @classmethod
    def is_safe(cls, user_input: str) -> bool:
        """
        Helper booleano rápido para verificação de segurança.
        Retorna True se seguro, False se violar regras de segurança.
        """
        safe, _ = cls.check_safety(user_input)
        return safe
