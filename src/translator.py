from __future__ import annotations

import logging
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat

logger = logging.getLogger("translator")

AGENTE_TRADUTOR = Agent(
    name="Tradutor",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "Traduza o conteudo abaixo para portugues brasileiro (PT-BR).",
        "Preserve blocos de codigo, comandos e exemplos exatamente como estao.",
        "Mantenha a estrutura Markdown original (cabecalhos, listas, tabelas).",
        "Nao adicione comentarios ou observacoes alem da traducao.",
    ],
    markdown=True,
)


def traduzir_arquivo(origem: Path, destino: Path) -> bool:
    if destino.exists():
        logger.info("  Pulando (ja traduzido): %s", destino.name)
        return True

    try:
        texto = origem.read_text(encoding="utf-8")
    except Exception as e:
        logger.error("  Erro ao ler %s: %s", origem.name, e)
        return False

    if not texto.strip():
        logger.warning("  Arquivo vazio: %s", origem.name)
        return False

    logger.info("  Traduzindo: %s", origem.name)
    try:
        resposta = AGENTE_TRADUTOR.run(texto)
        conteudo = resposta.content if hasattr(resposta, "content") else str(resposta)
    except Exception as e:
        logger.error("  Erro na traducao de %s: %s", origem.name, e)
        return False

    if not conteudo or len(conteudo.strip()) < 20:
        logger.warning("  Traducao vazia para %s", origem.name)
        return False

    destino.write_text(conteudo, encoding="utf-8")
    logger.info("  Salvo: %s (%d bytes)", destino.name, len(conteudo))
    return True


def traduzir_pasta(origem: Path, destino: Path) -> int:
    destino.mkdir(parents=True, exist_ok=True)
    md_files = sorted(origem.glob("*.md"))
    if not md_files:
        logger.warning("Nenhum arquivo .md encontrado em %s", origem)
        return 0

    logger.info("Traduzindo %d arquivos de %s", len(md_files), origem)
    sucessos = 0
    for md in md_files:
        nome_pt = (md.name[:-3] if md.name.endswith(".md") else md.name) + ".pt-BR.md"
        destino_path = destino / nome_pt
        if traduzir_arquivo(md, destino_path):
            sucessos += 1

    logger.info("Concluido: %d/%d traducoes", sucessos, len(md_files))
    return sucessos
