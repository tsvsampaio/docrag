# docrag

RAG sobre documentacao de frameworks Python, com traducao PT-BR e agente revisor de codigo.

## Stack

- **agno 2.x** — agentes com knowledge base + ferramentas
- **ChromaDB 1.5+** — vector store local
- **OpenAI GPT-4o-mini** — LLM principal
- **OpenAI text-embedding-3-small** — embedder

## Resultados

| Pipeline | Status | Detalhes |
|----------|--------|----------|
| Crawl | 1041/1041 paginas | docs.agno.com via httpx + lxml |
| Traducao PT-BR | 1041/1041 arquivos | GPT-4o-mini |
| Indexacao ChromaDB | 2 colecoes | `agno_docs_en` + `agno_docs_pt` |
| Expert Agent | Testado | Responde com base na KB |
| Reviewer Agent | Pronto | Le, linta e corrige codigo |

## Fluxo

```
crawl  →  translate  →  index  →  ask / review
```

## Comandos

```bash
# Via python direto
python cli.py crawl --site agno
python cli.py translate
python cli.py index
python cli.py ask "Como criar um Agent no agno?"
python cli.py review src/crawler.py

# Via uv run (entry points registrados)
uv run docrag crawl --site agno
uv run docrag translate
uv run docrag index
uv run docrag ask "Como criar um Agent no agno?"
uv run docrag review src/crawler.py
```

## Playground (Web UI)

Interface grafica interativa para conversar com os agentes no navegador.

```bash
uv run docrag playground
# Acessar: http://localhost:7777/playground
```

### Agentes Disponiveis

| Agente | Funcao |
|--------|--------|
| **Expert** | RAG sobre documentacao agno (PT-BR + EN) |
| **Revisor** | Le, linta e corrige codigo Python |
| **Tradutor** | Traduz Markdown para PT-BR |

## Setup rapido

```bash
uv venv --python 3.12
.venv\Scripts\activate
uv pip install -r requirements.txt
copy .env.example .env
# Edite .env com OPENAI_API_KEY
```

## Variaveis de Ambiente

```
OPENAI_API_KEY=sk-xxx      # obrigatorio (embedder + LLM)
TAVILY_API_KEY=tvly-xxx    # busca web (opcional)
```
