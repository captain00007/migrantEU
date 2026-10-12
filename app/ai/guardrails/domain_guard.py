from urllib.parse import urlparse
from app.core.config import settings

class DomainGuard:
    """
    Guardrail que restringe chamadas e buscas na web estritamente a fontes
    governamentais, acadêmicas oficiais e agências humanitárias reconhecidas.
    """
    OFFICIAL_DOMAINS_WHITELIST = {
        # Órgãos governamentais e de justiça
        "gov.br",
        "conare.justica.gov.br",
        "mec.gov.br",
        "defensoria.sp.def.br",
        "dpu.def.br",

        # Agências multilaterais e entidades humanitárias
        "acnur.org",
        "iom.int",
        "cbi.org.br",
        "caritas.org.br",
        "caritassp.org.br",
        "caritasrio.org.br",

        # Universidades brasileiras parceiras (CSVM/ACNUR, cotas e editais especiais)
        # Nota: Domínios com terminação .edu.br já são aceitos automaticamente por regra genérica.
        # Os domínios abaixo possuem terminação direta em .br:

        # Região Sul (PR, SC, RS)
        "ufpr.br",
        "ufsc.br",
        "ufrgs.br",
        "ufsm.br",
        "furg.br",
        "unisinos.br",
        "upf.br",
        "univates.br",
        "univali.br",
        "udesc.br",
        "uel.br",
        "uem.br",
        "uepg.br",
        "unicentro.br",
        "unioeste.br",
        "pucpr.br",
        "pucrs.br",

        # Região Sudeste (SP, RJ, MG, ES)
        "usp.br",
        "unicamp.br",
        "unesp.br",
        "unifesp.br",
        "ufscar.br",
        "ufrj.br",
        "uff.br",
        "uerj.br",
        "cefet-rj.br",
        "puc-rio.br",
        "pucsp.br",
        "unisantos.br",
        "mackenzie.br",
        "ufmg.br",
        "ufjf.br",
        "ufu.br",
        "ufv.br",
        "ufla.br",
        "pucminas.br",
        "ufes.br",
        "uvv.br",

        # Região Centro-Oeste (DF, GO, MS, MT)
        "unb.br",
        "ucb.br",
        "ufg.br",
        "ufms.br",
        "uems.br",
        "ufmt.br",

        # Região Nordeste (BA, PB, PE, CE, RN, AL, SE, PI, MA)
        "ufba.br",
        "uesb.br",
        "ufpb.br",
        "ufpe.br",
        "ufrpe.br",
        "uece.br",
        "ufc.br",
        "ufrn.br",
        "ufal.br",
        "ufs.br",
        "ufpi.br",
        "ufma.br",

        # Região Norte (RR, PA, AC, AP, RO)
        "ufrr.br",
        "ufpa.br",
        "ufac.br",
        "unifap.br",
        "unir.br"
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

            if settings.DOMAIN_GUARD_CUSTOM_DOMAINS:
                custom_domains = [d.strip().lower() for d in settings.DOMAIN_GUARD_CUSTOM_DOMAINS.split(",") if d.strip()]
                for cd in custom_domains:
                    if hostname == cd or hostname.endswith("." + cd):
                        return True

            return False
        except Exception:
            return False
