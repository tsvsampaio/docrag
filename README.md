# docrag

RAG sobre documentacao de frameworks Python, com suporte a multiplos sites, traducao PT-BR e agente revisor de codigo.

## Stack

- **agno** — agentes com knowledge base + ferramentas
- **ChromaDB** — vector store local
- **Groq** — inferencia LLM (llama-3.3-70b / openai/gpt-oss-120b)
- **crawl4ai** — crawler assincrono de documentacao
- **LangChain** — text splitters

## Fluxo

```
crawl  →  translate  →  index  →  ask / review
  M1          M2           M3         M4 / M5
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

## Setup

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env`:

```
GROQ_API_KEY=sua_chave_aqui
```

## Milestones

| Marco | Descricao | Status |
|-------|-----------|--------|
| M1 | Crawl — Extrair documentacao | Feito |
| M2 | Traducao PT-BR | Feito |
| M3 | Indexacao ChromaDB | Feito |
| M4 | Agente Especialista + CLI | Feito |
| M5 | Agente Revisor de Codigo | Feito |
| M6 | README e Deploy | Feito |

## Proximos Passos

- Suporte a mais sites (FastAPI, SQLAlchemy, etc.)
- Testes automatizados
- Deploy como servico (API FastAPI + frontend Streamlit)
