from urllib.parse import urlparse

class DomainGuard:
    """
    Guardrail que restringe chamadas e buscas na web estritamente a fontes
    governamentais, acadêmicas oficiais e agências humanitárias reconhecidas.
    """
    OFFICIAL_DOMAINS_WHITELIST = {
        "gov.br",
        "conare.justica.gov.br",
        "mec.gov.br",
        "acnur.org",
        "iom.int",
        "cbi.org.br",
        "caritas.org.br",
        "caritassp.org.br",
        "caritasrio.org.br",
        "defensoria.sp.def.br",
        "dpu.def.br"
    }

    @classmethod
    def is_url_allowed(cls, url: str, extra_domain: str | None = None) -> bool:
        if not url:
            return False
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            if not hostname:
                return False

            if hostname.endswith(".gov.br") or hostname.endswith(".edu.br"):
                return True

            for allowed in cls.OFFICIAL_DOMAINS_WHITELIST:
                if hostname == allowed or hostname.endswith("." + allowed):
                    return True

            if extra_domain:
                extra = extra_domain.lower().strip()
                if hostname == extra or hostname.endswith("." + extra):
                    return True

            return False
        except Exception:
            return False
