#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import dotenv

dotenv.load_dotenv()

DATA_DIR = Path(__file__).parent / "data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cli")


def cmd_crawl(args: argparse.Namespace) -> None:
    if args.site == "agno":
        from src.sites.agno import crawl

        total = asyncio.run(crawl())
        logger.info("Total crawleado: %d paginas", total)
    else:
        logger.error("Site desconhecido: %s", args.site)
        sys.exit(1)


def cmd_translate(args: argparse.Namespace) -> None:
    from src.translator import traduzir_pasta

    origem = DATA_DIR / "agno"
    destino = DATA_DIR / "agno_pt"
    total = traduzir_pasta(origem, destino)
    logger.info("Total traduzido: %d arquivos", total)


def cmd_index(args: argparse.Namespace) -> None:
    from src.indexer import indexar_tudo

    bases = indexar_tudo(limpar=args.limpar)
    for nome, kb in bases.items():
        if kb:
            logger.info("OK: %s", nome)
        else:
            logger.warning("Falha: %s", nome)


def cmd_ask(args: argparse.Namespace) -> None:
    from src.expert import criar_agente_expert

    agente = criar_agente_expert()
    pergunta = " ".join(args.pergunta)
    logger.info("Pergunta: %s", pergunta)
    resposta = agente.run(pergunta)
    print()
    print(resposta.content if hasattr(resposta, "content") else resposta)
    print()


def cmd_review(args: argparse.Namespace) -> None:
    from src.reviewer import criar_agente_revisor

    caminho = Path(args.arquivo).resolve()
    if not caminho.exists():
        logger.error("Arquivo nao encontrado: %s", caminho)
        sys.exit(1)

    agente = criar_agente_revisor()
    prompt = f"Revise o arquivo: {caminho}\n\nLeia o codigo, analise, execute linter e apresente o codigo corrigido."
    resposta = agente.run(prompt)
    print()
    print(resposta.content if hasattr(resposta, "content") else resposta)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="docrag — RAG sobre documentacao de frameworks Python"
    )
    sub = parser.add_subparsers(dest="comando")

    p_crawl = sub.add_parser("crawl", help="Crawlear documentacao de um site")
    p_crawl.add_argument(
        "--site",
        choices=["agno"],
        default="agno",
        help="Site para crawlear (default: agno)",
    )
    p_crawl.set_defaults(func=cmd_crawl)

    p_translate = sub.add_parser("translate", help="Traduzir docs crawleadas para PT-BR")
    p_translate.set_defaults(func=cmd_translate)

    p_index = sub.add_parser("index", help="Indexar docs traduzidas no ChromaDB")
    p_index.add_argument(
        "--limpar",
        action="store_true",
        help="Recriar colecoes do zero",
    )
    p_index.set_defaults(func=cmd_index)

    p_ask = sub.add_parser("ask", help="Perguntar ao agente especialista")
    p_ask.add_argument("pergunta", nargs="+", help="Sua pergunta sobre a documentacao")
    p_ask.set_defaults(func=cmd_ask)

    p_review = sub.add_parser("review", help="Revisar codigo com agente revisor")
    p_review.add_argument("arquivo", help="Caminho do arquivo para revisar")
    p_review.set_defaults(func=cmd_review)

    args = parser.parse_args()
    if args.comando is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
