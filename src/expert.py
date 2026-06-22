from __future__ import annotations

import logging
from agno.agent import Agent
from agno.knowledge.langchain import LangChainKnowledge
from agno.models.groq import Groq
from agno.vectordb.chroma import ChromaDb

from src.indexer import CHROMA_DIR

logger = logging.getLogger("expert")

_IDIOMA_INSTRUCAO = """Preferencia de idioma:
- Se a pergunta for em ingles, responda em ingles.
- Se a pergunta for em portugues, responda em portugues brasileiro.
- Use a base de conhecimento em portugues (agno_docs_pt) quando disponivel para questoes em PT-BR.
- Inclua exemplos de codigo sempre que relevante."""


def _carregar_kb(nome: str) -> LangChainKnowledge | None:
    chroma = ChromaDb(
        collection=nome,
        path=str(CHROMA_DIR),
    )

    knowledge = LangChainKnowledge(
        vector_db=chroma,
        num_documents=5,
    )
    return knowledge


def criar_agente_expert() -> Agent:
    kb_en = _carregar_kb("agno_docs_en")
    kb_pt = _carregar_kb("agno_docs_pt")

    knowledge = None
    if kb_en and kb_pt:
        knowledge = kb_en + kb_pt
    elif kb_en:
        knowledge = kb_en
    elif kb_pt:
        knowledge = kb_pt

    return Agent(
        name="Expert",
        model=Groq(id="openai/gpt-oss-120b"),
        knowledge=knowledge,
        instructions=[
            "Voce e um especialista em agno e desenvolvimento Python.",
            "Responda com base na documentacao indexada no ChromaDB.",
            _IDIOMA_INSTRUCAO,
            "Se a resposta nao estiver na KB, use seu conhecimento geral.",
            "Sempre formate blocos de codigo com syntax highlighting.",
        ],
        add_context=True,
        search_knowledge=True,
        markdown=True,
        debug_mode=False,
    )
