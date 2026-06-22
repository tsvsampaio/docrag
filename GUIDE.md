# docrag — Guia do Projeto

## O Que Fizemos

### 1. Criacao do Repositorio

- Repositorio GitHub: `github.com/tsvsampaio/docrag` (publico)
- Clone local em `C:\Users\neris\Desktop\Projetos\Depositorio_Caminhos\docrag`
- Autenticacao `gh auth login` concluida como usuario `tsvsampaio`

### 2. Planejamento em Milestones e Issues

Criamos **6 milestones** e **19 issues** no GitHub para rastrear todo o desenvolvimento:

| Milestone | Issues | Descricao |
|-----------|--------|-----------|
| **M1: Crawl** | #1 a #4 | Baixar llms.txt, crawlear todas as URLs com crawl4ai, salvar como .md |
| **M2: Traducao PT-BR** | #5 a #7 | Agente Groq que traduz .md → .pt-BR.md preservando codigo |
| **M3: Indexacao** | #11 a #13 | Carregar .pt-BR.md no ChromaDB via agno Knowledge |
| **M4: Especialista + CLI** | #14 a #16 | CLI argparse com agente que consulta 2 KB (en + pt) |
| **M5: Revisor de Codigo** | #8 a #10 | Agente com tools read_file + run_linter, retorna codigo corrigido |
| **M6: README e Deploy** | #17 a #19 | .gitignore, requirements.txt, README, commit/push final |

### 3. Implementacao dos Modulos

```
docrag/
├── .gitignore              # Pastas data/, chroma_db/, .env, __pycache__
├── requirements.txt        # agno, crawl4ai, groq, chromadb, langchain, httpx
├── pyproject.toml          # Configuracao basica do projeto
├── cli.py                  # Interface CLI com 5 subcomandos
│
├── src/
│   ├── crawler.py          # M1: Baixa llms.txt, crawleia paginas → .md
│   ├── translator.py       # M2: Agente Groq traduz .md → .pt-BR.md
│   ├── indexer.py          # M3: LangChain splitter + ChromaDb → Knowledge Base
│   ├── expert.py           # M4: Agente Expert combina KB en + pt
│   ├── reviewer.py         # M5: Agente Revisor com read_file + run_linter
│   └── sites/
│       └── agno.py         # Plug-in para docs.agno.com
```

**Detalhamento dos modulos:**

- **crawler.py** — Funcao assincrona `crawl_agno()` que:
  1. Faz GET em `https://docs.agno.com/llms.txt`
  2. Extrai todas as URLs de documentacao
  3. Crawleia cada pagina com `AsyncWebCrawler` (crawl4ai)
  4. Salva como `.md` em `data/agno/`
  5. Pula arquivos ja existentes (retomavel)

- **translator.py** — Agente `Tradutor` (Groq/llama-3.3-70b) que:
  1. Le cada `.md` de `data/agno/`
  2. Traduz para PT-BR preservando codigo e estrutura Markdown
  3. Salva como `.pt-BR.md` em `data/agno_pt/`
  4. Pula traducoes ja existentes

- **indexer.py** — Cria 2 colecoes no ChromaDB:
  - `agno_docs_en` — documentos originais em ingles
  - `agno_docs_pt` — documentos traduzidos
  - Usa `RecursiveCharacterTextSplitter` (chunk 2000, overlap 200)
  - Empacota como `LangChainKnowledge` para uso nos agentes

- **expert.py** — Agente `Expert` (Groq/openai-gpt-oss-120b) que:
  - Carrega as duas knowledge bases do ChromaDB
  - Combina com operador `+`
  - Detecta idioma da pergunta e responde no mesmo idioma
  - Prefere KB em portugues para perguntas PT-BR

- **reviewer.py** — Agente `Revisor` com 3 ferramentas:
  - `read_file(caminho)` — le arquivo de codigo
  - `run_linter(caminho)` — executa `ruff check`
  - `run_format_check(caminho)` — executa `ruff format --check`
  - Instrucao principal: retornar o **codigo corrigido completo**

- **cli.py** — 5 subcomandos argparse:
  - `crawl --site agno` — crawlear documentacao
  - `translate` — traduzir para PT-BR
  - `index [--limpar]` — indexar no ChromaDB
  - `ask <pergunta>` — perguntar ao especialista
  - `review <arquivo>` — revisar codigo

### 4. Decisoes de Arquitetura

| Decisao | Alternativa | Escolha | Motivo |
|---------|-------------|---------|--------|
| Formato de saida do crawl | .txt | **.md** | Preserva estrutura para chunking |
| Colecoes ChromaDB | Unica | **Duas (en + pt)** | Isolamento entre idiomas |
| Agente tradutor | Script local | **Agno Agent (Groq)** | Reaproveita infra existente |
| CLI vs pacote | pip install | **Script direto** | Simplicidade, sem build |
| Nomenclatura | CamelCase | **snake_case pt-BR** | Consistencia com automacao-fiscal |

### 5. Convencoes do Codigo

- `from __future__ import annotations` em todos os arquivos
- Logging com `logging.getLogger(__name__)` (logger por modulo)
- Codigo e comentarios em portugues
- Variaveis e funcoes em snake_case
- CLI via `argparse` com `subparsers` (mesmo padrao de `automacao-fiscal`)
- `dotenv.load_dotenv()` chamado no entrypoint (`cli.py`)

---

## Proximos Passos (Futuro)

### Curto Prazo

1. **Testar o pipeline completo**
   - `python cli.py crawl --site agno`
   - `python cli.py translate`
   - `python cli.py index`
   - `python cli.py ask "O que e um Agent?"`
   - `python cli.py review cli.py`

2. **Adicionar mais sites**
   - FastAPI (`https://fastapi.tiangolo.com/llms.txt`)
   - SQLAlchemy (`https://docs.sqlalchemy.org/llms.txt`)
   - LangChain
   - Cada site vira um arquivo em `src/sites/` com funcao `crawl()`

3. **Testes automatizados**
   - Testes unitarios para cada modulo (`tests/`)
   - Mock do `AsyncWebCrawler` para testes de crawler
   - Mock da API Groq para testes de traducao

### Medio Prazo

4. **Deploy como servico**
   - API FastAPI com endpoints: `/crawl`, `/translate`, `/index`, `/ask`, `/review`
   - Frontend Streamlit para interface web
   - Agendamento automatico de crawl (semanal)

5. **Melhorias nos agentes**
   - Cache de respostas frequentes
   - Suporte a multiplos modelos (via config)
   - Feedback loop: usuario avalia resposta, sistema ajusta

6. **CI/CD**
   - GitHub Actions para lint + testes
   - Deploy automatico em VPS ou Railway

### Longo Prazo

7. **RAG multi-site inteligente**
   - Agente decide qual site consultar baseado na pergunta
   - Indexacao incremental (apenas paginas modificadas)
   - Suporte a PDFs e video transcripts

8. **Modo offline**
   - Cache local de modelos (Groq -> LLM local via Ollama)
   - ChromaDB persistente totalmente offline

---

## Arquitetura (Diagrama Textual)

```
┌──────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐
│   Site   │───>│  Crawler  │───>│  .md en  │───>│ Translator │
│ llms.txt │    │ crawl4ai  │    │ data/agno│    │  Groq LLM  │
└──────────┘    └───────────┘    └──────────┘    └───────────┘
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
│  CLI/Web │    │ Expert    │    │  LangChainKnowledge       │
└──────────┘    └───────────┘    └──────────────────────────┘

┌──────────┐    ┌───────────┐
│  Arquivo │───>│  Revisor  │───> Codigo corrigido
│  .py     │    │ + linter  │
└──────────┘    └───────────┘
```

---

## Repositorio

- **URL:** `https://github.com/tsvsampaio/docrag`
- **Issues:** 19 criadas, distribuidas em 6 milestones
- **Milestones:** https://github.com/tsvsampaio/docrag/milestones

## Referencias

- [agno docs](https://docs.agno.com)
- [ChromaDB](https://docs.trychroma.com)
- [crawl4ai](https://docs.crawl4ai.com)
- [Groq](https://console.groq.com)
