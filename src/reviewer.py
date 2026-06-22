from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

logger = logging.getLogger("reviewer")


@tool(show_result=True)
def read_file(caminho: str) -> str:
    """Le o conteudo de um arquivo de codigo."""
    path = Path(caminho)
    if not path.exists():
        return f"Erro: arquivo nao encontrado: {caminho}"
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Erro ao ler {caminho}: {e}"


@tool(show_result=True)
def run_linter(caminho: str) -> str:
    """Executa ruff check no arquivo e retorna saida."""
    try:
        result = subprocess.run(
            ["ruff", "check", caminho],
            capture_output=True,
            text=True,
            timeout=30,
        )
        saida = result.stdout + result.stderr
        return saida.strip() if saida.strip() else "Nenhum problema encontrado."
    except FileNotFoundError:
        return "ruff nao encontrado. Instale com: pip install ruff"
    except Exception as e:
        return f"Erro ao executar linter: {e}"


@tool(show_result=True)
def run_format_check(caminho: str) -> str:
    """Verifica se o arquivo esta formatado corretamente com ruff format --check."""
    try:
        result = subprocess.run(
            ["ruff", "format", "--check", caminho],
            capture_output=True,
            text=True,
            timeout=30,
        )
        saida = result.stdout + result.stderr
        if result.returncode == 0:
            return "Arquivo ja esta formatado corretamente."
        return saida.strip() if saida.strip() else "Problemas de formatacao encontrados."
    except FileNotFoundError:
        return "ruff nao encontrado. Instale com: pip install ruff"
    except Exception as e:
        return f"Erro ao verificar formatacao: {e}"


@tool(show_result=True)
def run_syntax_check(caminho: str) -> str:
    """Verifica se o codigo Python tem erros de sintaxe sem executa-lo."""
    path = Path(caminho)
    if not path.exists():
        return f"Erro: arquivo nao encontrado: {caminho}"
    try:
        codigo_fonte = path.read_text(encoding="utf-8")
        compile(codigo_fonte, str(path), "exec")
        return "Nenhum erro de sintaxe encontrado."
    except SyntaxError as e:
        return f"Erro de sintaxe: {e}"
    except Exception as e:
        return f"Erro ao analisar sintaxe: {e}"


def criar_agente_revisor() -> Agent:
    return Agent(
        name="Revisor",
        model=OpenAIChat(id="gpt-4o"),
        tools=[read_file, run_linter, run_format_check, run_syntax_check],
        instructions=[
            "Voce e um revisor de codigo Python senior.",
            "Leia o arquivo, analise o codigo, e sugira melhorias.",
            "Apos analisar, execute o linter, formatador e syntax check para verificar problemas.",
            "Apresente o CODIGO CORRIGIDO completo (nao apenas trechos ou sugestoes).",
            "Explique as correcoes de forma concisa.",
            "Sempre retorne o codigo final pronto para copiar.",
        ],
        markdown=True,
        debug_mode=False,
    )
