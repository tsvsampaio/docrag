from __future__ import annotations

import logging

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.vectordb.chroma import ChromaDb

from src.indexer import CHROMA_DIR

logger = logging.getLogger("expert")

_IDIOMA_INSTRUCAO = """Preferencia de idioma:
- Se a pergunta for em ingles, responda em ingles.
- Se a pergunta for em portugues, responda em portugues brasileiro.
- Use a base de conhecimento em portugues (agno_docs_pt) quando disponivel para questoes em PT-BR.
- Inclua exemplos de codigo sempre que relevante."""


def _carregar_kb(nome: str) -> Knowledge | None:
    try:
        vector_db = ChromaDb(
            collection=nome,
            path=str(CHROMA_DIR),
            persistent_client=True,
        )
        return Knowledge(
            name=nome,
            vector_db=vector_db,
        )
    except Exception as e:
        logger.warning("Erro ao carregar KB '%s': %s", nome, e)
        return None


def criar_agente_expert() -> Agent:
    kb_pt = _carregar_kb("agno_docs_pt")
    kb_en = _carregar_kb("agno_docs_en")

    knowledge = kb_pt or kb_en

    return Agent(
        name="Expert",
        model=OpenAIChat(id="gpt-4o-mini"),
        knowledge=knowledge,
        instructions=[
            "Voce e um especialista em agno e desenvolvimento Python.",
            "Responda com base na documentacao indexada no ChromaDB.",
            _IDIOMA_INSTRUCAO,
            "Se a resposta nao estiver na KB, use seu conhecimento geral.",
            "Sempre formate blocos de codigo com syntax highlighting.",
        ],
        add_knowledge_to_context=True,
        search_knowledge=True,
        markdown=True,
        debug_mode=False,
    )
