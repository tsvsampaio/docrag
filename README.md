# docrag

RAG sobre documentacao de frameworks Python, com suporte a multiplos sites, traducao PT-BR e agente revisor de codigo.

## Stack

- **agno 2.x** — agentes com knowledge base + ferramentas
- **ChromaDB 1.5+** — vector store local
- **Groq** — inferencia LLM
- **OpenAI** — embedder
- **Tavily** — busca web

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
# Edite .env com GROQ_API_KEY e OPENAI_API_KEY
```

## Variaveis de Ambiente

```
GROQ_API_KEY=gsk_xxx       # obrigatorio
OPENAI_API_KEY=sk-xxx      # embedder padrao
TAVILY_API_KEY=tvly-xxx    # busca web (opcional)
```
