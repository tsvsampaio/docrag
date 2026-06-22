# Instalacao e Dependencias

## Ambiente

- **Python:** 3.14.3
- **Pip:** 25.3
- **SO:** Windows 11 (x64)
- **Venv:** `.venv\` na raiz do projeto

## Dependencias Diretas

| Pacote | Versao | Uso |
|--------|--------|-----|
| `agno` | >= 1.0.4 | Agentes com knowledge base |
| `crawl4ai` | >= 0.9.0 | Crawler assincrono de documentacao |
| `groq` | >= 0.7.0 | SDK Groq API |
| `chromadb` | >= 0.6.3 | Vector store local |
| `openai` | >= 2.43.0 | SDK OpenAI (usado internamente pelo agno) |
| `langchain` | >= 0.3.7 | Text splitters |
| `langchain-community` | >= 0.3.7 | Integracoes LangChain |
| `langchain-chroma` | >= 0.1.3 | ChromaDB para LangChain |
| `httpx` | >= 0.28.1 | HTTP client (llms.txt + chroma) |
| `python-dotenv` | >= 1.2.2 | Carregar .env |

## Dependencias Indiretas (resolvidas na instalacao)

```
aiohappyeyeballs==2.6.2    aiohttp==3.14.1            aiosignal==1.4.0
aiosqlite==0.22.1          alphashape==1.3.1          annotated-doc==0.0.4
annotated-types==0.7.0     anyio==4.14.0              attrs==26.1.0
beautifulsoup4==4.15.0     brotli==1.2.0              certifi==2026.6.17
cffi==2.0.0                chardet==7.4.3             charset-normalizer==3.4.7
click==8.4.1               click-log==0.4.0           colorama==0.4.6
cryptography==49.0.0       cssselect==1.4.0           distro==1.9.0
fastuuid==0.14.0           filelock==3.29.4           frozenlist==1.8.0
fsspec==2026.6.0           greenlet==3.5.2            h11==0.16.0
h2==4.3.0                  hpack==4.1.0               hf-xet==1.5.1
html2text==2024.2.26       httpcore==1.0.9            httpx==0.28.1
huggingface-hub==1.20.1    humanize==4.15.0           hyperframe==6.1.0
idna==3.18                 importlib-metadata==9.0.0  jiter==0.15.0
jinja2==3.1.6              joblib==1.5.3              jsonschema==4.26.0
jsonschema-specifications==2025.9.1  lark==1.3.1    lxml==5.4.0
markdown-it-py==4.2.0      markupsafe==3.0.3          mdurl==0.1.2
multidict==6.7.1           nltk==3.9.4                networkx==3.6.1
numpy==2.5.0               openai==2.43.0             packaging==26.2
patchright==1.60.1         pillow==12.2.0             playwright==1.60.0
playwright-stealth==2.0.3  propcache==0.5.2           psutil==7.2.2
pycparser==3.0             pydantic==2.13.4           pydantic-core==2.46.4
pyee==13.0.1               pygments==2.20.0           pyopenssl==26.3.0
pyyaml==6.0.3              rank-bm25==0.2.2           referencing==0.37.0
regex==2026.5.9            requests==2.34.2           rich==15.0.0
rpds-py==2026.5.1          rtree==1.4.1               scipy==1.18.0
shapely==2.1.2             shellingham==1.5.4         sniffio==1.3.1
snowballstemmer==2.2.0     soupsieve==2.8.4           tiktoken==0.13.0
tokenizers==0.23.1         tqdm==4.68.3               trimesh==4.12.2
typer==0.25.1              typing-extensions==4.15.0  typing-inspection==0.4.2
unclecode-litellm==1.81.13 urllib3==2.7.0             xxhash==3.7.0
yarl==1.24.2               zipp==4.1.0
```

## Instalacao

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate     # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar navegador para crawl4ai (Playwright)
python -m playwright install chromium
# Alternativa via patchright (incluido no crawl4ai):
patchright install chromium

# 4. Configurar .env
copy .env.example .env
# Edite .env com sua chave GROQ_API_KEY
```

## Ambiente Python 3.14

Python 3.14 requer wheels compilados. Alguns pacotes podem precisar de versoes mais recentes:

- **numpy:** >= 2.2.0 (wheel disponivel para cp314)
- **scipy:** >= 1.18.0 (wheel disponivel para cp314)
- **crawl4ai:** >= 0.9.0 (usa numpy sem restricao <2.1.1)

Se encontrar `error: metadata-generation-failed`, use `--only-binary=:all:`:

```bash
pip install --only-binary=:all: -r requirements.txt
```

## Estrutura de pastas apos instalacao

```
docrag/
├── .venv/               # Ambiente virtual
├── data/
│   ├── agno/            # Docs crawleadas (.md en)
│   └── agno_pt/         # Docs traduzidas (.pt-BR.md)
├── chroma_db/           # Banco ChromaDB persistente
└── ... demais arquivos ...
```
