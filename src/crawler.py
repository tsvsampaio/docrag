from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path

import httpx

logger = logging.getLogger("crawler")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

try:
    from crawl4ai import AsyncWebCrawler

    HAS_CRAWL4AI = True
except ImportError:
    HAS_CRAWL4AI = False

MAX_CONCURRENT = 20


def _normalizar_nome(url: str) -> str:
    nome = url.removeprefix("https://").removeprefix("http://")
    nome = nome.replace("/", "_").replace("?", "_").replace("=", "_")
    nome = re.sub(r"_+", "_", nome)
    nome = nome.strip("_")[:200]
    return (nome if nome.endswith(".md") else nome + ".md")


def _extrair_urls_llms_txt(url: str) -> list[str] | None:
    logger.info("Baixando llms.txt de %s", url)
    resp = httpx.get(url, follow_redirects=True, timeout=30)
    if resp.status_code != 200:
        logger.error("Falha ao baixar llms.txt: HTTP %d", resp.status_code)
        return None
    urls = []
    for linha in resp.text.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        m = re.match(r".*\((.+?)\)", linha)
        if m:
            urls.append(m.group(1))
    logger.info("%d URLs encontradas", len(urls))
    return urls


async def _baixar_url(client: httpx.AsyncClient, url: str, destino: Path) -> bool:
    caminho = destino / _normalizar_nome(url)
    if caminho.exists():
        return True

    try:
        resp = await client.get(url, follow_redirects=True, timeout=30)
        if resp.status_code != 200:
            logger.warning("  HTTP %d: %s", resp.status_code, url)
            return False

        try:
            from lxml import html as lh

            doc = lh.fromstring(resp.text)
            for tag in ("script", "style", "nav", "footer", "header"):
                for el in doc.xpath(f"//{tag}"):
                    el.drop_tree()
            main = doc.xpath("//main | //article | //body")
            elem = main[0] if main else doc
            texto = elem.text_content()
            linhas = [l.strip() for l in texto.splitlines() if l.strip()]
            conteudo = "\n\n".join(linhas)
        except ImportError:
            conteudo = resp.text

        if len(conteudo.strip()) < 50:
            logger.warning("  Conteudo muito curto: %s", url)
            return False

        caminho.write_text(conteudo, encoding="utf-8")
        logger.info("  OK: %s (%d bytes)", caminho.name, len(conteudo))
        return True
    except Exception as e:
        logger.error("  Erro ao baixar %s: %s", url, e)
        return False


async def _crawlear_lote(
    client: httpx.AsyncClient, urls: list[str], destino: Path
) -> int:
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def _limitada(url: str) -> bool:
        async with sem:
            return await _baixar_url(client, url, destino)

    tarefas = [_limitada(url) for url in urls]
    resultados = await asyncio.gather(*tarefas)
    return sum(1 for ok in resultados if ok)


async def crawl_agno(destino: Path | None = None) -> int:
    if destino is None:
        destino = DATA_DIR / "agno"
    destino.mkdir(parents=True, exist_ok=True)

    urls = _extrair_urls_llms_txt("https://docs.agno.com/llms.txt")
    if not urls:
        logger.error("Nenhuma URL para crawlear")
        return 0

    sucessos = 0

    if HAS_CRAWL4AI:
        async with AsyncWebCrawler() as crawler:
            sem = asyncio.Semaphore(MAX_CONCURRENT)

            async def _com_crawl4ai(url: str) -> bool:
                async with sem:
                    caminho = destino / _normalizar_nome(url)
                    if caminho.exists():
                        return True
                    try:
                        r = await crawler.arun(url=url, word_count_threshold=10)
                        c = r.markdown
                        if not c or len(c.strip()) < 50:
                            return False
                        caminho.write_text(c, encoding="utf-8")
                        logger.info("  OK: %s (%d bytes)", caminho.name, len(c))
                        return True
                    except Exception as e:
                        logger.error("  Erro: %s: %s", url, e)
                        return False

            tarefas = [_com_crawl4ai(url) for url in urls]
            for coro in asyncio.as_completed(tarefas):
                if await coro:
                    sucessos += 1
    else:
        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (compatible; docrag/0.2)"},
            timeout=30,
        ) as client:
            sucessos = await _crawlear_lote(client, urls, destino)

    logger.info(
        "Concluido: %d/%d paginas salvas em %s", sucessos, len(urls), destino
    )
    return sucessos
