import pytest
from app.ai.guardrails.domain_guard import DomainGuard
from app.ai.guardrails.safety_guard import SafetyGuard

@pytest.mark.unit
class TestDomainGuard:
    def test_allowed_official_government_domains(self):
        assert DomainGuard.is_url_allowed("https://www.gov.br/justica/conare") is True
        assert DomainGuard.is_url_allowed("https://conare.justica.gov.br/editais") is True
        assert DomainGuard.is_url_allowed("https://mec.gov.br/noticias") is True

    def test_allowed_educational_domains(self):
        # Domínios com final direto em .br da whitelist
        assert DomainGuard.is_url_allowed("https://www.ufpr.br/vestibular-refugiados") is True
        assert DomainGuard.is_url_allowed("https://usp.br/editais/csvm") is True
        assert DomainGuard.is_url_allowed("https://unicamp.br/vagas") is True
        assert DomainGuard.is_url_allowed("https://www.ufba.br/namir") is True
        assert DomainGuard.is_url_allowed("https://ufg.br/csvm") is True
        assert DomainGuard.is_url_allowed("https://uerj.br/noticias") is True
        assert DomainGuard.is_url_allowed("https://ufrr.br/ingresso") is True
        assert DomainGuard.is_url_allowed("https://ufu.br/editais") is True

        # Domínios com final em .edu.br (regra genérica)
        assert DomainGuard.is_url_allowed("https://www.unila.edu.br/editais") is True
        assert DomainGuard.is_url_allowed("https://uffs.edu.br/pro-imigrante") is True
        assert DomainGuard.is_url_allowed("https://ufam.edu.br/noticias") is True

    def test_allowed_humanitarian_domains(self):
        assert DomainGuard.is_url_allowed("https://www.acnur.org/portugues/dados") is True
        assert DomainGuard.is_url_allowed("https://brazil.iom.int/programas") is True
        assert DomainGuard.is_url_allowed("https://caritas.org.br/acolhimento") is True
        assert DomainGuard.is_url_allowed("https://www.dpu.def.br/assistencia") is True

    def test_blocked_arbitrary_domains(self):
        assert DomainGuard.is_url_allowed("https://google.com") is False
        assert DomainGuard.is_url_allowed("https://malicious-site.com/edital") is False
        assert DomainGuard.is_url_allowed("http://localhost:8080") is False
        assert DomainGuard.is_url_allowed("") is False

    def test_institution_custom_domain(self):
        assert DomainGuard.is_url_allowed("https://instituto-parceiro.org/vaga", extra_domain="instituto-parceiro.org") is True

@pytest.mark.unit
class TestSafetyGuard:
    def test_cpf_masking(self):
        user_input = "Meu CPF é 123.456.789-00 preciso saber sobre vestibular"
        sanitized = SafetyGuard.sanitize_input(user_input)
        assert "123.456.789-00" not in sanitized
        assert "[CPF PROTEGIDO]" in sanitized

    def test_empty_and_null_bytes(self):
        assert SafetyGuard.sanitize_input("") == ""
        input_with_null = "Vestibular" + chr(0) + " UFPR"
        assert chr(0) not in SafetyGuard.sanitize_input(input_with_null)
