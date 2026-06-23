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
- `OpenAIChat("gpt-4o-mini")` + Knowledge em PT-BR (lazy loading)
- `search_knowledge=True` e `add_knowledge_to_context=False` (evita busca duplicada)
- Detecta idioma da pergunta e responde no mesmo idioma
- **Melhoria:** Conexao com ChromaDB via `LazyChromaDb` — so conecta na primeira consulta
- **Testado** — respondeu corretamente sobre "O que e agno e como criar um agente?"

#### Reviewer Agent (M5)
- `OpenAIChat("gpt-4o-mini")` com 3 tools:
  - `read_file(caminho)` — le arquivo de codigo
  - `run_linter(caminho)` — executa `ruff check`
  - `run_format_check(caminho)` — executa `ruff format --check`
- Instrucao principal: retornar o **codigo corrigido completo**
- Corrigido para usar `OpenAIChat` (estava `Groq`)

### 7. CLI

```bash
# Via python direto
python cli.py crawl --site agno   # M1
python cli.py translate           # M2
python cli.py index               # M3
python cli.py ask "pergunta"      # M4
python cli.py review arquivo.py   # M5

# Via uv run (entry point registrado no pyproject.toml)
uv run docrag crawl --site agno
uv run docrag translate
uv run docrag index
uv run docrag ask "pergunta"
uv run docrag review arquivo.py
```

### 8. Playground (Web UI)

O **agno playground** oferece uma interface web interativa para conversar com os agentes.

```bash
# Iniciar o playground
uv run docrag playground
# ou: uv run docrag-playground

# Opcoes:
uv run docrag playground --port 7777              # porta personalizada
uv run docrag playground --host 0.0.0.0 --port 80 # expor na rede
uv run docrag playground --reload                 # auto-reload em dev
```

Acessar no navegador: `http://localhost:7777` (retorna JSON com metadados)

> **Nota:** O `AgentOS` do agno nao possui frontend embutido. Para usar a interface web, conecte-se pelo [Agno Playground](https://app.agno.com) apontando para `http://localhost:7777`, ou use um cliente HTTP como `httpx` ou `curl` para interagir com a API.

#### Agentes Disponiveis no Playground

| Agente | Nome | Modelo | Funcao |
|--------|------|--------|--------|
| **Expert** | `Expert` | GPT-4o-mini | RAG sobre documentacao agno (PT-BR + EN) |
| **Revisor** | `Revisor` | GPT-4o | Le, linta (`ruff`), formata e corrige codigo Python |
| **Tradutor** | `Tradutor` | GPT-4o-mini | Traduz documentacao Markdown para PT-BR |

#### Arquivos do Playground

| Arquivo | Descricao |
|---------|-----------|
| `src/playground_app.py` | Cria o app FastAPI com `AgentOS` expondo os 3 agentes |
| `src/cli.py` | Comando `playground` com `--host`, `--port`, `--reload` |
| `pyproject.toml` | Entry points `docrag` e `docrag-playground` |

### 9. Melhorias de Performance e Estabilidade (Jun/2026)

#### 9.1 Lazy Loading do ChromaDB

**Problema:** O ChromaDB era carregado no momento da importacao dos modulos (`import src.expert`),
levando ~6s para conectar em cada colecao. Com duas colecoes (en + pt), o startup do servidor
demorava ~12s apenas para conectar ao banco vetorial.

**Solucao:** Criado o wrapper `LazyChromaDb` (`src/expert.py`) que adia a conexao com o
ChromaDB para o momento da primeira busca (`search()`). Os metodos `exists()` e `create()`
foram sobrescritos para retornar `True` e `pass`, respectivamente, evitando que o
`Knowledge.__post_init__()` dispare a conexao prematuramente.

```python
class LazyChromaDb:
    def _obter(self):
        if self._db is None:
            self._db = ChromaDb(collection=..., path=..., persistent_client=True)
        return self._db

    def exists(self): return True   # ChromaDB ja populado
    def create(self): pass          # Nao precisa recriar
    def search(self, query, **kwargs): return self._obter().search(query=query, ...)
```

**Impacto:** Reducao de ~12s para ~0s no startup do servidor (a conexao ocorre apenas
na primeira pergunta do usuario).

#### 9.2 Eliminacao de Busca Redundante na KB

**Problema:** O agente Expert estava configurado com `add_knowledge_to_context=True` E
`search_knowledge=True`, fazendo com que a base de conhecimento fosse consultada **duas
vezes** a cada pergunta — uma para montar o contexto inicial e outra durante a execucao
do agente.

**Solucao:** Alterado `add_knowledge_to_context=False` em `src/expert.py`, mantendo apenas
`search_knowledge=True`. O agente agora pesquisa a KB apenas quando necessario, durante a
geracao da resposta.

**Impacto:** Eliminacao de uma chamada de embedding + busca ChromaDB por pergunta (~5-7s
economizados).

#### 9.3 Feedback Visual no CLI

**Problema:** Os comandos `ask` e `review` ficavam ate 30s sem qualquer saida no terminal,
dando a impressao de que o sistema havia congelado.

**Solucao:** Adicionados logs de progresso em `src/cli.py`:

```
21:30:31 [INFO] Carregando agente Expert...
21:30:41 [INFO] Agente carregado em 9.5s
21:30:41 [INFO] Pergunta: What is agno
21:30:41 [INFO] Consultando base de conhecimento e LLM...
21:31:05 [INFO] Resposta recebida em 33.5s
```

**Impacto:** Usuario ve o progresso em cada etapa, eliminando a sensacao de
"congelamento".

#### 9.4 Desativacao de Telemetria

**Problema:** O `AgentOS` enviava dados de telemetria para `os-api.agno.com` a cada
inicializacao e a cada execucao de agente, adicionando ~1-2s de latencia e
dependencia de rede externa.

**Solucao:** Adicionado `telemetry=False` na criacao do `AgentOS` em
`src/playground_app.py`.

**Impacto:** Eliminacao de chamadas de rede desnecessarias e maior privacidade.

#### 9.5 Reducao de Colecoes Carregadas

**Problema:** O `criar_agente_expert()` carregava as duas colecoes (`agno_docs_en` +
`agno_docs_pt`) mesmo quando apenas uma seria usada.

**Solucao:** Alterado para carregar apenas `agno_docs_pt` (priorizando o portugues
brasileiro). Caso a pergunta seja em ingles, o LLM tem conhecimento geral para
responder.

**Impacto:** Startup mais rapido e menor uso de memoria.

---

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
| CLI vs pacote | pip install | **Script direto + entry points** | `uv run docrag <cmd>` via `pyproject.toml` |
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

1. ~~**Testar o agente Revisor**~~ — **Concluido**
2. ~~**Feedback visual no CLI**~~ — **Concluido**: Logs de progresso em `ask` e `review`
3. ~~**Lazy loading ChromaDB**~~ — **Concluido**: Startup ~12x mais rapido
4. **Adicionar mais sites** — FastAPI, SQLAlchemy, LangChain
5. **Testes automatizados** — `tests/` com mocks

### Medio Prazo

6. ~~**Deploy como servico**~~ — **Concluido**: Playground agno via `uv run docrag playground`
7. ~~**Melhorias nos agentes**~~ — **Concluido**: Lazy ChromaDB, eliminacao de buscas duplicadas, telemetria desligada
8. **Cache de consultas** — evitar re-embeddings para perguntas similares
9. **CI/CD** — GitHub Actions

### Longo Prazo

10. **RAG multi-site inteligente** — agente decide qual site consultar
11. **Modo offline** — Ollama + ChromaDB local

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
