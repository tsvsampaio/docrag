# docrag — Guia do Projeto

## O Que Fizemos

### 1. Criacao do Repositorio

- Repositorio GitHub: `github.com/tsvsampaio/docrag` (publico)
- Clone local em `C:\Users\neris\Desktop\Projetos\Depositorio_Caminhos\docrag`

### 2. Dependencias com uv

- Python 3.12.11 em venv gerenciado por `uv`
- 140+ pacotes instalados via `uv pip install -r requirements.txt`
- Stack principal: agno 2.x, ChromaDB 1.5+, OpenAI, lxml

### 3. Crawl — M1

- **1041/1041 paginas** baixadas de `https://docs.agno.com/llms.txt`
- Duas estrategias: `crawl4ai` (se instalado) ou fallback `httpx.AsyncClient` + `lxml`
- Semaphore(20) para controle de concorrencia
- Arquivados como `.md` em `data/agno/`
- Funcao `_normalizar_nome()` usa replace de `/`, `?`, `=` por `_` e garante extensao `.md` unica
- **Bug corrigido**: extensao `.md.md` duplicada — agora so anexa `.md` se o nome nao terminar em `.md`

### 4. Traducao PT-BR — M2

- **Primeira tentativa**: `Groq`/`llama-3.3-70b-versatile` — rate limit free tier (100k TPD) atingido apos ~30 arquivos
- **Segunda tentativa**: `OpenAIChat`/`gpt-4o-mini` — sucesso em **1041/1041 arquivos**
- Preserva blocos de codigo, comandos e estrutura Markdown
- Salva como `{nome}.pt-BR.md` em `data/agno_pt/`
- Custo estimado: ~3M tokens (inteiramente no usuario)
- **Bug corrigido**: nome do arquivo destino usava `.replace(".md", ".pt-BR.md")` que quebrava nomes com `.md` no meio; substituido por `rsplit(".md", 1)`

### 5. Indexacao ChromaDB — M3

- **2 colecoes** criadas em `chroma_db/`:
  - `agno_docs_en` — documentos originais em ingles (1041 arquivos)
  - `agno_docs_pt` — documentos traduzidos (1041 arquivos)
- Usa `agno 2.x Knowledge` + `ChromaDb` com embedder OpenAI `text-embedding-3-small`
- Persistencia local via `persistent_client=True`

### 6. Agentes — M4 e M5

#### Expert Agent (M4)
- `OpenAIChat("gpt-4o-mini")` + Knowledge combinada (prioriza PT-BR)
- `add_knowledge_to_context=True` em vez do antigo `add_context`
- Detecta idioma da pergunta e responde no mesmo idioma
- **Testado apos correcao** — respondeu corretamente sobre "O que e agno e como criar um agente?"

#### Reviewer Agent (M5)
- `OpenAIChat("gpt-4o-mini")` com 3 tools:
  - `read_file(caminho)` — le arquivo de codigo
  - `run_linter(caminho)` — executa `ruff check`
  - `run_format_check(caminho)` — executa `ruff format --check`
- Instrucao principal: retornar o **codigo corrigido completo**
- Corrigido para usar `OpenAIChat` (estava `Groq`)

### 7. CLI

```bash
python cli.py crawl --site agno   # M1
python cli.py translate           # M2
python cli.py index               # M3
python cli.py ask "pergunta"      # M4
python cli.py review arquivo.py   # M5
```

## Arquitetura (Diagrama Textual)

```
┌──────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐
│   Site   │───>│  Crawler  │───>│  .md en  │───>│ Translator │
│ llms.txt │    │ httpx+crawl│    │ data/agno│    │  gpt-4o-   │
└──────────┘    └───────────┘    └──────────┘    │   mini     │
                                                  └───────────┘
                                                        │
                                                        ▼
                                                ┌───────────┐
                                                │ .pt-BR.md │
                                                │data/agno_pt│
                                                └───────────┘
                                                        │
                                                        ▼
┌──────────┐    ┌───────────┐    ┌──────────────────────────┐
│  Usuario │<───│  Agente   │<───│  ChromaDB (en + pt)      │
│  CLI     │    │ Expert    │    │  agno 2.x Knowledge       │
└──────────┘    └───────────┘    └──────────────────────────┘

┌──────────┐    ┌───────────┐
│  Arquivo │───>│  Revisor  │───> Codigo corrigido
│  .py     │    │ + linter  │
└──────────┘    └───────────┘
```

## Decisoes de Arquitetura

| Decisao | Alternativa | Escolha | Motivo |
|---------|-------------|---------|--------|
| LLM | Groq llama-3.3-70b | **OpenAI GPT-4o-mini** | Rate limit Groq free tier inviavel |
| Crawler | So crawl4ai | **httpx + fallback lxml** | Evita dependencia pesada de Playwright |
| Colecoes ChromaDB | Unica | **Duas (en + pt)** | Isolamento entre idiomas |
| CLI vs pacote | pip install | **Script direto** | Simplicidade, sem build |
| Nomenclatura | CamelCase | **snake_case pt-BR** | Consistencia com automacao-fiscal |

## Convencoes do Codigo

- `from __future__ import annotations` em todos os arquivos
- Logging com `logging.getLogger(__name__)` (logger por modulo)
- Codigo e comentarios em portugues
- Variaveis e funcoes em snake_case
- CLI via `argparse` com `subparsers`
- `dotenv.load_dotenv()` chamado no entrypoint (`cli.py`)

## Proximos Passos (Futuro)

### Curto Prazo

1. **Testar o agente Revisor** com `python cli.py review cli.py`
2. **Adicionar mais sites** — FastAPI, SQLAlchemy, LangChain
3. **Testes automatizados** — `tests/` com mocks

### Medio Prazo

4. **Deploy como servico** — FastAPI + frontend Streamlit
5. **Melhorias nos agentes** — cache, multi-modelo, feedback loop
6. **CI/CD** — GitHub Actions

### Longo Prazo

7. **RAG multi-site inteligente** — agente decide qual site consultar
8. **Modo offline** — Ollama + ChromaDB local

## Variaveis de Ambiente

```bash
OPENAI_API_KEY=sk-xxx       # obrigatorio (embedder + LLM)
TAVILY_API_KEY=tvly-xxx     # busca web (opcional)
```

## Repositorio

- **URL:** `https://github.com/tsvsampaio/docrag`
- **Status:** Pipeline completo executado e testado

## Referencias

- [agno docs](https://docs.agno.com)
- [ChromaDB](https://docs.trychroma.com)
- [OpenAI](https://platform.openai.com)
