import pytest
from unittest.mock import MagicMock
from app.services.notice_service import NoticeService

@pytest.mark.integration
class TestNoticeService:
    async def test_list_active_notices_with_institutions_mapping(self, mock_supabase):
        mock_supabase["select"].return_value = MagicMock(data=[
            {
                "id": "notice-1",
                "category_id": "cat-uuid-1",
                "title": "Vestibular Especial 2026",
                "category": "ensino_superior",
                "end_date": "2026-12-31",
                "institutions": {
                    "name": "Universidade Federal do Paraná",
                    "sigla": "UFPR",
                    "uf": "PR",
                    "city": "Curitiba",
                    "official_domain": "ufpr.br"
                },
                "categories": {
                    "id": "cat-uuid-1",
                    "slug": "ensino_superior",
                    "name": "Ensino Superior (Graduação)",
                    "badge_color": "blue"
                }
            }
        ])

        notices = await NoticeService.list_active_notices(category="ensino_superior", uf="PR")
        assert len(notices) == 1
        assert notices[0]["institution_name"] == "Universidade Federal do Paraná"
        assert notices[0]["institution_sigla"] == "UFPR"
        assert notices[0]["institution_uf"] == "PR"
        assert notices[0]["category_slug"] == "ensino_superior"
        assert notices[0]["category_name"] == "Ensino Superior (Graduação)"

    async def test_approve_notice_triggers_status_update(self, mock_supabase, monkeypatch):
        mock_supabase["update"].return_value = MagicMock(data=[
            {
                "id": "notice-99",
                "institution_id": "inst-1",
                "category_id": "cat-uuid-2",
                "title": "Curso PLAC",
                "category": "curso_portugues",
                "summary": "Curso de português",
                "end_date": "2026-11-30",
                "notice_url": "https://ufpr.br/plac",
                "status": "aprovado_vigente"
            }
        ])

        # Mock de busca de instituição, de categoria e de assinantes
        mock_supabase["select"].side_effect = [
            MagicMock(data=[{"id": "inst-1", "name": "UFPR", "sigla": "UFPR"}]),
            MagicMock(data=[{"id": "cat-uuid-2", "slug": "curso_portugues", "name": "Cursos de Português (PLAC)"}]),
            MagicMock(data=[{"email": "migrante@exemplo.com", "topics": ["curso_portugues"]}])
        ]

        result = await NoticeService.approve_notice("notice-99")
        assert result["notice"]["status"] == "aprovado_vigente"
        assert result["emails_dispatched"] >= 0

    async def test_list_categories(self, mock_supabase):
        mock_supabase["select"].return_value = MagicMock(data=[
            {"id": "cat-1", "slug": "ensino_superior", "name": "Ensino Superior (Graduação)", "badge_color": "blue", "is_active": True},
            {"id": "cat-2", "slug": "curso_portugues", "name": "Cursos de Português (PLAC)", "badge_color": "emerald", "is_active": True}
        ])

        categories = await NoticeService.list_categories()
        assert len(categories) == 2
        assert categories[0]["slug"] == "ensino_superior"
