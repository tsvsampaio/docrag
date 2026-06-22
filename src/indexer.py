from __future__ import annotations

import logging
from pathlib import Path

from agno.knowledge.langchain import LangChainKnowledge
from agno.vectordb.chroma import ChromaDb
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger("indexer")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"


def _criar_knowledge_base(
    nome: str,
    pasta_docs: Path,
    limpar: bool = False,
) -> LangChainKnowledge | None:
    if not pasta_docs.exists():
        logger.warning("Pasta nao encontrada: %s", pasta_docs)
        return None

    md_files = sorted(pasta_docs.glob("*.md"))
    if not md_files:
        logger.warning("Nenhum .md em %s", pasta_docs)
        return None

    logger.info("Indexando %d arquivos de %s", len(md_files), pasta_docs)
    textos = []
    nomes = []
    for md in md_files:
        try:
            textos.append(md.read_text(encoding="utf-8"))
            nomes.append(md.name)
        except Exception as e:
            logger.warning("Erro ao ler %s: %s", md.name, e)

    if not textos:
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )

    chroma = ChromaDb(
        collection=nome,
        path=str(CHROMA_DIR),
    )

    knowledge = LangChainKnowledge(
        vector_db=chroma,
        splitter=text_splitter,
        num_documents=5,
    )

    knowledge.load_documents(textos, filenames=nomes)
    logger.info(
        "Knowledge base '%s' populada em %s", nome, CHROMA_DIR
    )
    return knowledge


def indexar_tudo(limpar: bool = False) -> dict[str, LangChainKnowledge | None]:
    return {
        "agno_docs_en": _criar_knowledge_base(
            "agno_docs_en", DATA_DIR / "agno", limpar
        ),
        "agno_docs_pt": _criar_knowledge_base(
            "agno_docs_pt", DATA_DIR / "agno_pt", limpar
        ),
    }
