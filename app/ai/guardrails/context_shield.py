"""
ContextShield: Mecanismo de segurança defensiva para LLMs contra Direct e Indirect Prompt Injection.
Implementa separação rígida entre Instruções e Dados (Data vs. Instructions) utilizando
encapsulamento XML com blocos CDATA e sanitização de escape.
"""

from typing import List, Dict, Any, Optional

class ContextShield:
    """
    Guardião de contexto que encapsula entradas do usuário e dados externos recuperados (RAG / Web)
    em tags XML com blocos CDATA, impedindo que textos maliciosos sejam interpretados como instruções.
    """

    @classmethod
    def sanitize_cdata(cls, text: str) -> str:
        """
        Sanitiza o conteúdo prevenindo quebras de bloco CDATA ao substituir ']]>' por ']]&gt;'.
        """
        if not text:
            return ""
        return str(text).replace("]]>", "]]&gt;").strip()

    @classmethod
    def format_user_query(cls, query: str) -> str:
        """
        Encapsula a pergunta do usuário em tag XML CDATA segura.
        Garante que instruções ou tentativas de jailbreak contidas na consulta sejam tratadas
        estritamente como dados passivos de entrada, e nunca como ordens do sistema.
        """
        safe_query = cls.sanitize_cdata(query)
        return f"<user_query>\n  <![CDATA[\n{safe_query}\n  ]]>\n</user_query>"

    @classmethod
    def format_document(
        cls,
        doc_id: str,
        content: str,
        title: str = "",
        url: str = "",
        source: str = "WEB_OFFICIAL"
    ) -> str:
        """
        Encapsula um documento ou trecho externo em tag <document> com bloco CDATA seguro.
        Neutraliza tentativas de Indirect Prompt Injection embutidas em páginas ou editais.
        """
        safe_content = cls.sanitize_cdata(content)
        safe_title = str(title or "").replace('"', '&quot;')
        safe_url = str(url or "").replace('"', '&quot;')
        return (
            f'  <document id="{doc_id}" source="{source}" title="{safe_title}" url="{safe_url}">\n'
            f'    <![CDATA[\n{safe_content}\n  ]]>\n'
            f'  </document>'
        )

    @classmethod
    def build_knowledge_base(
        cls,
        local_docs: Optional[List[Dict[str, Any]]] = None,
        web_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Consolida documentos do banco local e resultados web em uma base XML/CDATA unificada e segura,
        conforme especificação ContextShield (Data vs. Instructions).
        """
        local_docs = local_docs or []
        web_results = web_results or []
        doc_elements = []

        for idx, doc in enumerate(local_docs, start=1):
            doc_id = str(doc.get("id") or f"local_{idx}")
            title = str(doc.get("title") or "")
            url = str(doc.get("notice_url") or doc.get("url") or "")
            content = str(doc.get("summary") or doc.get("content") or "")
            safe_content = cls.sanitize_cdata(content)
            doc_elements.append(
                f'  <document id="{doc_id}" source="LOCAL_CACHE" title="{title}" url="{url}">\n'
                f'    <![CDATA[\n{safe_content}\n  ]]>\n'
                f'  </document>'
            )

        for idx, res in enumerate(web_results, start=1):
            doc_id = str(res.get("id") or f"web_{idx}")
            title = str(res.get("title") or "")
            url = str(res.get("url") or "")
            content = str(res.get("content") or "")
            safe_content = cls.sanitize_cdata(content)
            doc_elements.append(
                f'  <document id="{doc_id}" source="WEB_OFFICIAL" title="{title}" url="{url}">\n'
                f'    <![CDATA[\n{safe_content}\n  ]]>\n'
                f'  </document>'
            )

        xml_body = "\n".join(doc_elements)
        return (
            f'<official_knowledge_base count="{len(local_docs) + len(web_results)}">\n'
            f'{xml_body}\n'
            f'</official_knowledge_base>'
        )

    @classmethod
    def format_live_reader_content(cls, url: str, question: str, text_content: str) -> str:
        """
        Formata o conteúdo extraído ao vivo de editais e páginas web para proteger o modelo
        contra injeção indireta presente no corpo de arquivos PDF ou HTML.
        """
        safe_text = cls.sanitize_cdata(text_content)
        safe_url = str(url or "").replace('"', '&quot;')
        safe_q = str(question or "").replace('"', '&quot;')
        return (
            f'<official_extracted_content url="{safe_url}" query="{safe_q}">\n'
            f'  <![CDATA[\n{safe_text}\n  ]]>\n'
            f'</official_extracted_content>'
        )
