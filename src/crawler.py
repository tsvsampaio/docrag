from __future__ import annotations

import logging
import re
from pathlib import Path

import httpx

logger = logging.getLogger("crawler")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# crawl4ai e opcional — fornece renderizacao JS e extracao superior
try:
    from crawl4ai import AsyncWebCrawler

    HAS_CRAWL4AI = True
except ImportError:
    HAS_CRAWL4AI = False


def _normalizar_nome(url: str) -> str:
    nome = url.removeprefix("https://").removeprefix("http://")
    nome = nome.replace("/", "_").replace("?", "_").replace("=", "_")
    nome = re.sub(r"_+", "_", nome)
    return nome.strip("_")[:200] + ".md"


def _extrair_urls_llms_txt(url: str) -> list[str] | None:
    logger.info("Baixando llms.txt de %s", url)
    resp = httpx.get(url, follow_redirects=True, timeout=30)
    if resp.status_code != 200:
        logger.error("Falha ao baixar llms.txt: HTTP %d", resp.status_code)
        return None
    urls = []
    for linha in resp.text.splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and linha.startswith("http"):
            urls.append(linha)
    logger.info("%d URLs encontradas", len(urls))
    return urls


async def _crawlear_com_crawl4ai(url: str, destino: Path) -> bool:
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        try:
            resultado = await crawler.arun(url=url, word_count_threshold=10)
            conteudo = resultado.markdown
            if not conteudo or len(conteudo.strip()) < 50:
                logger.warning("  Conteudo muito curto: %s", url)
                return False
            caminho = destino / _normalizar_nome(url)
            caminho.write_text(conteudo, encoding="utf-8")
            logger.info("  OK: %s (%d bytes)", caminho.name, len(conteudo))
            return True
        except Exception as e:
            logger.error("  Erro ao crawlear %s: %s", url, e)
            return False


def _extrair_markdown_simples(html: str) -> str:
    from lxml import html as lh

    doc = lh.fromstring(html)
    for tag in ("script", "style", "nav", "footer", "header"):
        for el in doc.xpath(f"//{tag}"):
            el.drop_tree()
    main = doc.xpath("//main | //article | //body")
    elem = main[0] if main else doc
    texto = elem.text_content()
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    return "\n\n".join(linhas)


async def _crawlear_com_httpx(url: str, destino: Path) -> bool:
    caminho = destino / _normalizar_nome(url)
    if caminho.exists():
        logger.info("  Pulando (ja existe): %s", caminho.name)
        return True

    try:
        resp = httpx.get(url, follow_redirects=True, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; docrag/0.2)"
        })
        if resp.status_code != 200:
            logger.warning("  HTTP %d: %s", resp.status_code, url)
            return False

        try:
            from lxml import html

            conteudo = _extrair_markdown_simples(resp.text)
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


async def crawl_agno(destino: Path | None = None) -> int:
    if destino is None:
        destino = DATA_DIR / "agno"
    destino.mkdir(parents=True, exist_ok=True)

    urls = _extrair_urls_llms_txt("https://docs.agno.com/llms.txt")
    if not urls:
        logger.error("Nenhuma URL para crawlear")
        return 0

    sucessos = 0
    for url in urls:
        if HAS_CRAWL4AI:
            ok = await _crawlear_com_crawl4ai(url, destino)
        else:
            ok = await _crawlear_com_httpx(url, destino)
        if ok:
            sucessos += 1

    logger.info("Concluido: %d/%d paginas salvas em %s", sucessos, len(urls), destino)
    return sucessos
