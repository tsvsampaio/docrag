from __future__ import annotations

import logging
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat

from src.indexer import CHROMA_DIR

logger = logging.getLogger("expert")

_IDIOMA_INSTRUCAO = """Preferencia de idioma:
- Se a pergunta for em ingles, responda em ingles.
- Se a pergunta for em portugues, responda em portugues brasileiro.
- Use a base de conhecimento em portugues (agno_docs_pt) quando disponivel para questoes em PT-BR.
- Inclua exemplos de codigo sempre que relevante."""


class LazyChromaDb:
    """Envolucro que adia a conexao com ChromaDB ate a primeira busca."""

    def __init__(self, collection: str, path: str | Path) -> None:
        self._collection = collection
        self._path = str(path)
        self._db = None

    def _obter(self):
        if self._db is None:
            from agno.vectordb.chroma import ChromaDb

            logger.info("Conectando ao ChromaDB (lazy): %s", self._collection)
            self._db = ChromaDb(
                collection=self._collection,
                path=self._path,
                persistent_client=True,
            )
        return self._db

    def exists(self):
        return True

    def create(self):
        pass

    def search(self, query: str, **kwargs):
        return self._obter().search(query=query, **kwargs)

    def __getattr__(self, name: str):
        return getattr(self._obter(), name)


def _carregar_kb_lazy(nome: str) -> Knowledge | None:
    try:
        vector_db = LazyChromaDb(
            collection=nome,
            path=CHROMA_DIR,
        )
        return Knowledge(
            name=nome,
            vector_db=vector_db,
        )
    except Exception as e:
        logger.warning("Erro ao criar KB lazy '%s': %s", nome, e)
        return None


def criar_agente_expert() -> Agent:
    kb_pt = _carregar_kb_lazy("agno_docs_pt")

    knowledge = kb_pt

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
        add_knowledge_to_context=False,
        search_knowledge=True,
        markdown=True,
        debug_mode=False,
    )
