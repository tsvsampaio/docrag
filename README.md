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
# 1. Crawlear documentacao
python cli.py crawl --site agno

# 2. Traduzir para PT-BR
python cli.py translate

# 3. Indexar no ChromaDB
python cli.py index

# 4. Perguntar ao especialista
python cli.py ask "Como criar um Agent no agno?"

# 5. Revisar codigo
python cli.py review src/crawler.py
```

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
