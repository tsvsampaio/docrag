from __future__ import annotations

import logging
from pathlib import Path

from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb

logger = logging.getLogger("indexer")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"


def _criar_knowledge_base(
    nome: str,
    pasta_docs: Path,
) -> Knowledge | None:
    if not pasta_docs.exists():
        logger.warning("Pasta nao encontrada: %s", pasta_docs)
        return None

    md_files = sorted(pasta_docs.glob("*.md")) + sorted(pasta_docs.glob("*.pt-BR.md"))
    if not md_files:
        md_files = sorted(pasta_docs.rglob("*"))
    if not md_files:
        logger.warning("Nenhum arquivo em %s", pasta_docs)
        return None

    logger.info("Indexando %s de %s", nome, pasta_docs)

    vector_db = ChromaDb(
        collection=nome,
        path=str(CHROMA_DIR),
        persistent_client=True,
    )

    knowledge = Knowledge(
        name=nome,
        vector_db=vector_db,
    )

    knowledge.insert(path=str(pasta_docs))
    logger.info("Knowledge base '%s' populada em %s", nome, CHROMA_DIR)
    return knowledge


def indexar_tudo() -> dict[str, Knowledge | None]:
    return {
        "agno_docs_en": _criar_knowledge_base(
            "agno_docs_en", DATA_DIR / "agno"
        ),
        "agno_docs_pt": _criar_knowledge_base(
            "agno_docs_pt", DATA_DIR / "agno_pt"
        ),
    }
