from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path

import httpx
from crawl4ai import AsyncWebCrawler

logger = logging.getLogger("crawler")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LLMS_TXT_URL = "https://docs.agno.com/llms.txt"


def _normalizar_nome(url: str) -> str:
    nome = url.removeprefix("https://").removeprefix("http://")
    nome = nome.replace("/", "_").replace("?", "_").replace("=", "_")
    nome = re.sub(r"_+", "_", nome)
    return nome.strip("_")[:200] + ".md"


def _carregar_llms_txt() -> list[str] | None:
    logger.info("Baixando llms.txt de %s", LLMS_TXT_URL)
    resp = httpx.get(LLMS_TXT_URL, follow_redirects=True, timeout=30)
    if resp.status_code != 200:
        logger.error("Falha ao baixar llms.txt: HTTP %d", resp.status_code)
        return None
    urls = []
    for linha in resp.text.splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and linha.startswith("http"):
            urls.append(linha)
    logger.info("%d URLs encontradas em llms.txt", len(urls))
    return urls


async def _crawlear_url(
    crawler: AsyncWebCrawler, url: str, destino: Path
) -> tuple[str, bool]:
    nome_arquivo = _normalizar_nome(url)
    caminho = destino / nome_arquivo
    if caminho.exists():
        logger.info("  Pulando (ja existe): %s", nome_arquivo)
        return url, True

    try:
        resultado = await crawler.arun(url=url, word_count_threshold=10)
        conteudo = resultado.markdown
        if not conteudo or len(conteudo.strip()) < 50:
            logger.warning("  Conteudo muito curto: %s", url)
            return url, False
        caminho.write_text(conteudo, encoding="utf-8")
        logger.info("  OK: %s (%d bytes)", nome_arquivo, len(conteudo))
        return url, True
    except Exception as e:
        logger.error("  Erro ao crawlear %s: %s", url, e)
        return url, False


async def crawl_agno(destino: Path | None = None) -> int:
    if destino is None:
        destino = DATA_DIR / "agno"
    destino.mkdir(parents=True, exist_ok=True)

    urls = _carregar_llms_txt()
    if not urls:
        logger.error("Nenhuma URL para crawlear")
        return 0

    sucessos = 0
    async with AsyncWebCrawler() as crawler:
        tarefas = [_crawlear_url(crawler, url, destino) for url in urls]
        for coro in asyncio.as_completed(tarefas):
            _, ok = await coro
            if ok:
                sucessos += 1

    logger.info("Concluido: %d/%d paginas salvas em %s", sucessos, len(urls), destino)
    return sucessos
