import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.ai.intent import IntentClassifier, INTENTS_MAP
from app.ai.prompts.specialized import get_prompt_for_intent, PROMPTS_BY_INTENT
from app.ai.agent import get_tools_for_intent, process_chat_message

@pytest.mark.unit
class TestIntentClassifier:

    @pytest.mark.asyncio
    async def test_detects_ensino_superior(self):
        mock_response = MagicMock()
        mock_response.content = "ensino_superior"
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response

        with patch("app.ai.intent.LLMFactory.get_llm", return_value=mock_llm):
            res = await IntentClassifier.detect_intent("Como fazer vestibular na UFPR?")
            assert res["key"] == "ensino_superior"
            assert "Graduação" in res["action_label"]

    @pytest.mark.asyncio
    async def test_detects_curso_portugues(self):
        mock_response = MagicMock()
        mock_response.content = "curso_portugues"
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response

        with patch("app.ai.intent.LLMFactory.get_llm", return_value=mock_llm):
            res = await IntentClassifier.detect_intent("Je voudrais apprendre le portugais")
            assert res["key"] == "curso_portugues"
            assert "Idioma" in res["action_label"]

    @pytest.mark.asyncio
    async def test_detects_documentacao_refugio(self):
        mock_response = MagicMock()
        mock_response.content = "documentacao_refugio"
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response

        with patch("app.ai.intent.LLMFactory.get_llm", return_value=mock_llm):
            res = await IntentClassifier.detect_intent("Como agendar na Polícia Federal para renovar protocolo?")
            assert res["key"] == "documentacao_refugio"
            assert "CONARE" in res["action_label"]

    @pytest.mark.asyncio
    async def test_detects_comunidades(self):
        mock_response = MagicMock()
        mock_response.content = "comunidades"
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response

        with patch("app.ai.intent.LLMFactory.get_llm", return_value=mock_llm):
            res = await IntentClassifier.detect_intent("Existe associação de refugiados afegãos?")
            assert res["key"] == "comunidades"
            assert "Associações" in res["action_label"]

    @pytest.mark.asyncio
    async def test_detects_geral_acolhimento(self):
        mock_response = MagicMock()
        mock_response.content = "geral_acolhimento"
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_response

        with patch("app.ai.intent.LLMFactory.get_llm", return_value=mock_llm):
            res = await IntentClassifier.detect_intent("Olá, bom dia!")
            assert res["key"] == "geral_acolhimento"

    @pytest.mark.asyncio
    async def test_fallback_when_llm_fails(self):
        with patch("app.ai.intent.LLMFactory.get_llm", side_effect=Exception("API down")):
            res = await IntentClassifier.detect_intent("Alguma pergunta")
            assert res["key"] == "geral_acolhimento"

    def test_parse_key_resilience(self):
        assert IntentClassifier._parse_key("ENSINO_SUPERIOR") == "ensino_superior"
        assert IntentClassifier._parse_key("```json\n{\"intent\": \"curso_portugues\"}\n```") == "curso_portugues"
        assert IntentClassifier._parse_key("desconhecido") == "geral_acolhimento"

    def test_specialized_prompts_loaded(self):
        for intent_key in INTENTS_MAP.keys():
            prompt = get_prompt_for_intent(intent_key)
            assert len(prompt) > 100
            assert "migrantEU" in prompt

    def test_prompts_are_modular_and_do_not_mix_domains(self):
        prompt_ensino = get_prompt_for_intent("ensino_superior")
        assert "ENSINO SUPERIOR" in prompt_ensino
        assert "CURSOS DE PORTUGUÊS" not in prompt_ensino
        assert "REGULARIZAÇÃO DOCUMENTAL" not in prompt_ensino
        assert "COMUNIDADES, ASSOCIAÇÕES" not in prompt_ensino

        prompt_comunidades = get_prompt_for_intent("comunidades")
        assert "COMUNIDADES" in prompt_comunidades
        assert "VESTIBULARES E REVALIDAÇÃO" not in prompt_comunidades
        assert "Celpe-Bras" not in prompt_comunidades

        prompt_portugues = get_prompt_for_intent("curso_portugues")
        assert "LÍNGUA DE ACOLHIMENTO" in prompt_portugues
        assert "Sisconare" not in prompt_portugues

    def test_tools_are_modular_per_intent(self):
        tools_ensino = get_tools_for_intent("ensino_superior")
        tool_names_ensino = [t.name for t in tools_ensino]
        assert "check_cached_notices_tool" in tool_names_ensino
        assert "search_communities_tool" not in tool_names_ensino

        tools_comunidades = get_tools_for_intent("comunidades")
        tool_names_comunidades = [t.name for t in tools_comunidades]
        assert "search_communities_tool" in tool_names_comunidades
        assert "check_cached_notices_tool" not in tool_names_comunidades

    @pytest.mark.asyncio
    async def test_out_of_scope_early_stops_without_running_second_llm(self):
        with patch("app.ai.agent.IntentClassifier.detect_intent", return_value={"key": "fora_de_escopo"}):
            with patch("app.ai.agent.get_migranteu_agent") as mock_get_agent:
                reply = await process_chat_message("Quem ganhou a copa do mundo de futebol?")
                assert "fora deste escopo" in reply or "migrantEU" in reply
                # O segundo LLM (AgentExecutor) NUNCA deve ser invocado!
                mock_get_agent.assert_not_called()
